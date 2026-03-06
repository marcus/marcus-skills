# Lightroom Indexer Script

Complete Python script that reads a Lightroom CC catalog and builds a searchable SQLite+FTS5 index.

## How the Catalog Works

Lightroom CC stores its data in a SQLite database (the `.mcat` file) with two key tables:
- `docs` — document records, each with a `fullDocId` and a `winningRevSequence`
- `revs` — revision content stored as **msgpack**-encoded blobs

Each document revision contains a msgpack dict with fields like `type`, `captureDate`, `ratings`, `xmp`, `importSource`, etc. The indexer unpacks these and extracts structured metadata.

## Script

```python
#!/usr/bin/env python3
"""Lightroom Library Index -- searchable SQLite+FTS5 index of Lightroom CC catalog."""

import argparse
import json
import os
import random as random_mod
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

import msgpack

# ── Config ──────────────────────────────────────────────────────────────
# Edit these paths to match your setup:

# Path to Lightroom's internal catalog database
CATALOG_PATH = os.path.expanduser(
    "~/Pictures/Lightroom Library.lrlibrary/<YOUR-CATALOG-ID>/Managed Catalog.mcat"
)

# Where original photo files live (for --with-path resolution)
ORIGINALS_BASE = "/path/to/Lightroom/originals/<YOUR-CATALOG-ID>/originals"

# Where to write the search index database
DB_PATH = "/path/to/lightroom.db"

# ── Schema ──────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    doc_id TEXT,
    filename TEXT,
    file_ext TEXT,
    is_edited INTEGER DEFAULT 0,
    capture_date TEXT,
    capture_year INTEGER,
    capture_month INTEGER,
    rating INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    camera_make TEXT,
    camera_model TEXT,
    lens TEXT,
    focal_length_35mm INTEGER,
    iso INTEGER,
    shutter_speed TEXT,
    aperture REAL,
    content_type TEXT,
    file_size INTEGER,
    sha256 TEXT,
    type TEXT,
    subtype TEXT,
    imported_at TEXT,
    updated_at TEXT,
    raw_keywords TEXT,
    catalog_rev_sequence INTEGER,
    indexed_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS keywords (
    asset_id TEXT REFERENCES assets(id),
    keyword TEXT NOT NULL,
    PRIMARY KEY (asset_id, keyword)
);

CREATE TABLE IF NOT EXISTS albums (
    id TEXT PRIMARY KEY,
    name TEXT,
    subtype TEXT,
    parent_id TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS album_assets (
    album_id TEXT REFERENCES albums(id),
    asset_id TEXT REFERENCES assets(id),
    PRIMARY KEY (album_id, asset_id)
);

CREATE TABLE IF NOT EXISTS ingest_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_assets_rating ON assets(rating);
CREATE INDEX IF NOT EXISTS idx_assets_capture_date ON assets(capture_date);
CREATE INDEX IF NOT EXISTS idx_assets_capture_year ON assets(capture_year);
CREATE INDEX IF NOT EXISTS idx_assets_is_edited ON assets(is_edited);
CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
"""

FTS_SCHEMA = """
CREATE VIRTUAL TABLE IF NOT EXISTS assets_fts USING fts5(
    asset_id,
    filename,
    keywords,
    camera_info
);
"""


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    conn.executescript(FTS_SCHEMA)
    conn.commit()
    return conn


def safe_get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return default
        if d is None:
            return default
    return d


def parse_capture_date(date_str):
    if not date_str:
        return None, None, None
    try:
        clean = str(date_str).replace('T', ' ').split('+')[0].split('Z')[0].split('.')[0]
        dt = datetime.fromisoformat(clean)
        return dt.strftime('%Y-%m-%d'), dt.year, dt.month
    except Exception:
        return None, None, None


def resolve_origin_path(filename, capture_date):
    """Resolve file path in originals directory (organized by year/date)."""
    if not filename or not capture_date:
        return None
    try:
        dt = datetime.fromisoformat(str(capture_date))
        year = str(dt.year)
        date_dir = dt.strftime('%Y-%m-%d')
        return os.path.join(ORIGINALS_BASE, year, date_dir, filename)
    except Exception:
        return None


def extract_asset(data, doc_id, rev_sequence):
    """Extract asset metadata from msgpack data."""
    dtype = safe_get(data, 'type', default='')
    subtype = safe_get(data, 'subtype', default='')

    if dtype != 'asset':
        return None, None

    asset_id = safe_get(data, 'importSource', 'originalName') or safe_get(data, 'id') or doc_id

    # Filename
    filename = safe_get(data, 'importSource', 'fileName', default='')
    file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    is_edited = 1 if '-Edit.' in filename else 0

    # Capture date
    capture_date_raw = safe_get(data, 'captureDate')
    capture_date, capture_year, capture_month = parse_capture_date(capture_date_raw)

    # Rating — take max across devices. Structure: {'device_id': {'rating': N}}
    ratings = safe_get(data, 'ratings', default={})
    rating = 0
    if isinstance(ratings, dict) and ratings:
        for v in ratings.values():
            if isinstance(v, dict):
                r = v.get('rating', 0)
            elif isinstance(v, (int, float)):
                r = v
            else:
                continue
            if isinstance(r, (int, float)) and r > rating:
                rating = int(r)

    # Dimensions (prefer cropped)
    width = safe_get(data, 'croppedWidth') or safe_get(data, 'width')
    height = safe_get(data, 'croppedHeight') or safe_get(data, 'height')

    # XMP / EXIF metadata
    xmp = safe_get(data, 'xmp', default={})
    tiff = safe_get(xmp, 'tiff', default={})
    exif = safe_get(xmp, 'exif', default={})
    aux = safe_get(xmp, 'aux', default={})

    camera_make = safe_get(tiff, 'Make')
    camera_model = safe_get(tiff, 'Model')
    lens = safe_get(aux, 'Lens')
    focal_length_35mm = safe_get(exif, 'FocalLengthIn35mmFilm')
    iso_val = safe_get(exif, 'ISOSpeedRatings')
    if isinstance(iso_val, list):
        iso_val = iso_val[0] if iso_val else None
    shutter_speed = safe_get(exif, 'ExposureTime')
    aperture = safe_get(exif, 'FNumber')
    if isinstance(aperture, list):
        aperture = aperture[0] if aperture else None
    if isinstance(shutter_speed, list):
        shutter_speed = shutter_speed[0] if shutter_speed else None
    if isinstance(focal_length_35mm, list):
        focal_length_35mm = focal_length_35mm[0] if focal_length_35mm else None

    # Keywords from XMP dc:subject
    subject = safe_get(xmp, 'dc', 'subject', default={})
    kw_list = []
    if isinstance(subject, dict):
        kw_list = [k for k, v in subject.items() if v]
    elif isinstance(subject, list):
        kw_list = subject

    content_type = safe_get(data, 'contentType', default='')
    file_size = safe_get(data, 'fileSize')
    sha256 = safe_get(data, 'sha256')
    imported_at = safe_get(data, 'importTimestamp')
    updated_at = safe_get(data, 'userUpdated')

    asset = {
        'id': doc_id,
        'doc_id': doc_id,
        'filename': filename,
        'file_ext': file_ext,
        'is_edited': is_edited,
        'capture_date': capture_date,
        'capture_year': capture_year,
        'capture_month': capture_month,
        'rating': rating,
        'width': width,
        'height': height,
        'camera_make': camera_make,
        'camera_model': camera_model,
        'lens': lens,
        'focal_length_35mm': focal_length_35mm,
        'iso': iso_val,
        'shutter_speed': str(shutter_speed) if shutter_speed else None,
        'aperture': float(aperture) if aperture and not isinstance(aperture, (list, dict)) else None,
        'content_type': content_type,
        'file_size': file_size,
        'sha256': sha256,
        'type': dtype,
        'subtype': subtype,
        'imported_at': imported_at,
        'updated_at': updated_at,
        'raw_keywords': json.dumps(kw_list) if kw_list else None,
        'catalog_rev_sequence': rev_sequence,
    }

    return asset, kw_list


def cmd_ingest(args):
    full = args.full
    conn = init_db()

    last_seq = 0
    if not full:
        row = conn.execute("SELECT value FROM ingest_meta WHERE key='last_sequence'").fetchone()
        if row:
            last_seq = int(row[0])

    if full:
        conn.execute("DELETE FROM assets")
        conn.execute("DELETE FROM keywords")
        conn.execute("DELETE FROM assets_fts")
        conn.execute("DELETE FROM albums")
        conn.execute("DELETE FROM album_assets")
        conn.commit()
        last_seq = 0

    cat = sqlite3.connect(f"file:{CATALOG_PATH}?mode=ro", uri=True)
    cat.text_factory = bytes

    if last_seq > 0:
        total = cat.execute(
            "SELECT COUNT(*) FROM docs d JOIN revs r ON d.winningRevSequence = r.sequence WHERE r.sequence > ?",
            (last_seq,)
        ).fetchone()[0]
        cursor = cat.execute(
            "SELECT d.fullDocId, r.content, r.sequence FROM docs d JOIN revs r ON d.winningRevSequence = r.sequence WHERE r.sequence > ? ORDER BY r.sequence",
            (last_seq,)
        )
    else:
        total = cat.execute(
            "SELECT COUNT(*) FROM docs d JOIN revs r ON d.winningRevSequence = r.sequence"
        ).fetchone()[0]
        cursor = cat.execute(
            "SELECT d.fullDocId, r.content, r.sequence FROM docs d JOIN revs r ON d.winningRevSequence = r.sequence ORDER BY r.sequence"
        )

    print(f"Processing {total} revisions (from seq {last_seq})...", file=sys.stderr)

    assets_batch = []
    kw_batch = []
    fts_batch = []
    max_seq = last_seq
    count = 0
    errors = 0

    for i, (doc_id_raw, content_raw, seq) in enumerate(cursor):
        if seq > max_seq:
            max_seq = seq

        try:
            doc_id = doc_id_raw.decode('utf-8', errors='replace') if isinstance(doc_id_raw, bytes) else str(doc_id_raw)
            data = msgpack.unpackb(content_raw, raw=False)
        except Exception:
            errors += 1
            continue

        asset, kw_list = extract_asset(data, doc_id, seq)
        if not asset:
            continue

        count += 1
        assets_batch.append(asset)

        for kw in kw_list:
            kw_batch.append((asset['id'], kw))

        camera_info = ' '.join(filter(None, [asset['camera_make'], asset['camera_model'], asset['lens']]))
        fts_batch.append((asset['id'], asset['filename'], ' '.join(kw_list), camera_info))

        if len(assets_batch) >= 10000:
            _flush(conn, assets_batch, kw_batch, fts_batch, is_full=full)
            assets_batch, kw_batch, fts_batch = [], [], []
            print(f"  {i+1}/{total} processed, {count} assets...", file=sys.stderr)

    if assets_batch:
        _flush(conn, assets_batch, kw_batch, fts_batch, is_full=full)

    conn.execute("INSERT OR REPLACE INTO ingest_meta VALUES ('last_sequence', ?)", (str(max_seq),))
    conn.execute("INSERT OR REPLACE INTO ingest_meta VALUES ('last_ingest', ?)", (datetime.now().isoformat(),))
    conn.commit()
    conn.close()
    cat.close()

    result = {"ok": True, "assets_indexed": count, "total_revisions": total, "errors": errors, "max_sequence": max_seq}
    print(json.dumps(result, indent=2))


def _flush(conn, assets, kws, fts, is_full=False):
    cols = ['id', 'doc_id', 'filename', 'file_ext', 'is_edited', 'capture_date', 'capture_year',
            'capture_month', 'rating', 'width', 'height', 'camera_make', 'camera_model', 'lens',
            'focal_length_35mm', 'iso', 'shutter_speed', 'aperture', 'content_type', 'file_size',
            'sha256', 'type', 'subtype', 'imported_at', 'updated_at', 'raw_keywords', 'catalog_rev_sequence']
    placeholders = ','.join(['?'] * len(cols))
    col_str = ','.join(cols)

    conn.executemany(
        f"INSERT OR REPLACE INTO assets ({col_str}) VALUES ({placeholders})",
        [tuple(a[c] for c in cols) for a in assets]
    )
    if not is_full:
        asset_ids = [a['id'] for a in assets]
        conn.executemany("DELETE FROM keywords WHERE asset_id=?", [(a,) for a in asset_ids])
        conn.executemany("DELETE FROM assets_fts WHERE asset_id=?", [(a,) for a in asset_ids])
    conn.executemany("INSERT OR IGNORE INTO keywords (asset_id, keyword) VALUES (?,?)", kws)
    conn.executemany("INSERT INTO assets_fts (asset_id, filename, keywords, camera_info) VALUES (?,?,?,?)", fts)
    conn.commit()


def _build_search_query(query, rating=None, rating_exact=None, year=None, edited=False,
                        camera=None, lens=None, date=None, date_from=None, date_to=None):
    conditions = []
    params = []

    if query and query != '*':
        conditions.append("a.id IN (SELECT asset_id FROM assets_fts WHERE assets_fts MATCH ?)")
        params.append(query)

    if rating is not None:
        conditions.append("a.rating >= ?")
        params.append(rating)
    if rating_exact is not None:
        conditions.append("a.rating = ?")
        params.append(rating_exact)
    if year:
        conditions.append("a.capture_year = ?")
        params.append(year)
    if edited:
        conditions.append("a.is_edited = 1")
    if camera:
        conditions.append("(a.camera_model LIKE ? OR a.camera_make LIKE ?)")
        params.extend([f'%{camera}%', f'%{camera}%'])
    if lens:
        conditions.append("a.lens LIKE ?")
        params.append(f'%{lens}%')
    if date:
        conditions.append("a.capture_date LIKE ?")
        params.append(f'{date}%')
    if date_from:
        conditions.append("a.capture_date >= ?")
        params.append(f'{date_from}')
    if date_to:
        conditions.append("a.capture_date < ?")
        params.append(f'{date_to}T99')

    where = " AND ".join(conditions) if conditions else "1=1"
    return where, params


def _format_result(row, with_path=False):
    r = {
        'id': row[0], 'filename': row[1], 'capture_date': row[2],
        'rating': row[3], 'camera_model': row[4], 'lens': row[5],
        'is_edited': bool(row[6]),
        'keywords': json.loads(row[7]) if row[7] else [],
    }
    if with_path:
        path = resolve_origin_path(row[1], row[2])
        r['origin_path'] = path
        r['file_available'] = os.path.exists(path) if path else False
    return r


def cmd_search(args):
    conn = sqlite3.connect(DB_PATH)
    where, params = _build_search_query(
        args.query, rating=args.rating, rating_exact=getattr(args, 'rating_exact', None),
        year=args.year, edited=args.edited, camera=args.camera, lens=args.lens,
        date=getattr(args, 'date', None), date_from=getattr(args, 'date_from', None),
        date_to=getattr(args, 'date_to', None)
    )

    sql = f"""SELECT a.id, a.filename, a.capture_date, a.rating, a.camera_model, a.lens,
              a.is_edited, a.raw_keywords
              FROM assets a WHERE {where} ORDER BY a.rating DESC, a.capture_date DESC LIMIT ?"""
    params.append(args.limit)

    rows = conn.execute(sql, params).fetchall()
    results = [_format_result(r, args.with_path) for r in rows]

    output = {
        "ok": True, "query": args.query,
        "filters": {k: v for k, v in {'rating_min': args.rating, 'year': args.year,
                    'edited': args.edited or None, 'camera': args.camera, 'lens': args.lens}.items() if v},
        "count": len(results), "results": results
    }
    print(json.dumps(output, indent=2))
    conn.close()


def cmd_stats(args):
    conn = sqlite3.connect(DB_PATH)
    stats = {}
    stats['total_assets'] = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    stats['rated'] = conn.execute("SELECT COUNT(*) FROM assets WHERE rating > 0").fetchone()[0]
    stats['edited'] = conn.execute("SELECT COUNT(*) FROM assets WHERE is_edited = 1").fetchone()[0]
    stats['with_keywords'] = conn.execute("SELECT COUNT(DISTINCT asset_id) FROM keywords").fetchone()[0]
    stats['unique_keywords'] = conn.execute("SELECT COUNT(DISTINCT keyword) FROM keywords").fetchone()[0]

    stats['ratings'] = {}
    for row in conn.execute("SELECT rating, COUNT(*) FROM assets GROUP BY rating ORDER BY rating"):
        stats['ratings'][str(row[0])] = row[1]

    stats['top_cameras'] = []
    for row in conn.execute("SELECT camera_model, COUNT(*) c FROM assets WHERE camera_model IS NOT NULL GROUP BY camera_model ORDER BY c DESC LIMIT 10"):
        stats['top_cameras'].append({'model': row[0], 'count': row[1]})

    stats['years'] = {}
    for row in conn.execute("SELECT capture_year, COUNT(*) FROM assets WHERE capture_year IS NOT NULL GROUP BY capture_year ORDER BY capture_year"):
        stats['years'][str(row[0])] = row[1]

    meta = conn.execute("SELECT value FROM ingest_meta WHERE key='last_ingest'").fetchone()
    stats['last_ingest'] = meta[0] if meta else None

    print(json.dumps({"ok": True, "stats": stats}, indent=2))
    conn.close()


def cmd_keywords(args):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT keyword, COUNT(*) c FROM keywords GROUP BY keyword ORDER BY c DESC LIMIT ?",
        (args.top,)
    ).fetchall()
    result = [{"keyword": r[0], "count": r[1]} for r in rows]
    print(json.dumps({"ok": True, "count": len(result), "keywords": result}, indent=2))
    conn.close()


def cmd_random(args):
    conn = sqlite3.connect(DB_PATH)
    conditions = ["a.rating > 0"]
    params = []
    if args.rating:
        conditions.append("a.rating >= ?")
        params.append(args.rating)
    if args.keyword:
        conditions.append("a.id IN (SELECT asset_id FROM keywords WHERE keyword LIKE ?)")
        params.append(f'%{args.keyword}%')

    where = " AND ".join(conditions)
    count = conn.execute(f"SELECT COUNT(*) FROM assets a WHERE {where}", params).fetchone()[0]
    if count == 0:
        print(json.dumps({"ok": True, "result": None, "message": "No matching photos"}))
        return

    offset = random_mod.randint(0, count - 1)
    row = conn.execute(
        f"""SELECT a.id, a.filename, a.capture_date, a.rating, a.camera_model, a.lens,
            a.is_edited, a.raw_keywords FROM assets a WHERE {where} LIMIT 1 OFFSET ?""",
        params + [offset]
    ).fetchone()

    result = _format_result(row, with_path=True)
    print(json.dumps({"ok": True, "total_matching": count, "result": result}, indent=2))
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Lightroom Library Index')
    sub = parser.add_subparsers(dest='command')

    p_ingest = sub.add_parser('ingest')
    p_ingest.add_argument('--full', action='store_true')

    p_search = sub.add_parser('search')
    p_search.add_argument('query')
    p_search.add_argument('--rating', type=int)
    p_search.add_argument('--rating-exact', type=int)
    p_search.add_argument('--year', type=int)
    p_search.add_argument('--edited', action='store_true')
    p_search.add_argument('--camera')
    p_search.add_argument('--lens')
    p_search.add_argument('--date', help='Filter by date (YYYY-MM-DD)')
    p_search.add_argument('--date-from', help='Filter from date inclusive (YYYY-MM-DD)')
    p_search.add_argument('--date-to', help='Filter to date inclusive (YYYY-MM-DD)')
    p_search.add_argument('--limit', type=int, default=20)
    p_search.add_argument('--format', default='json')
    p_search.add_argument('--with-path', action='store_true')

    p_stats = sub.add_parser('stats')

    p_kw = sub.add_parser('keywords')
    p_kw.add_argument('--top', type=int, default=50)

    p_rand = sub.add_parser('random')
    p_rand.add_argument('--rating', type=int)
    p_rand.add_argument('--keyword')

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {'ingest': cmd_ingest, 'search': cmd_search, 'stats': cmd_stats,
     'keywords': cmd_keywords, 'random': cmd_random}[args.command](args)


if __name__ == '__main__':
    main()
```
