---
name: lightroom-search
description: Search and query a Lightroom CC photo catalog via a SQLite+FTS5 index. Use when the user wants to find photos, browse their library, get stats, search by keyword/rating/camera/date, or work with Lightroom catalog data. Covers catalog location, indexing, search queries, and the index database schema.
---

# Lightroom Catalog Search

Search a Lightroom CC catalog through a SQLite+FTS5 index built from Adobe's internal msgpack-based catalog.

## How It Works

Lightroom CC stores its catalog as a SQLite database containing msgpack-encoded document revisions. The indexer reads these revisions, extracts photo metadata (EXIF, keywords, ratings, etc.), and writes them into a searchable SQLite database with full-text search.

**Two databases are involved:**
1. **Lightroom's catalog** (read-only source) — the `.mcat` file inside the `.lrlibrary` bundle
2. **The search index** (created by the indexer) — a regular SQLite DB you query against

## Catalog Location

The Lightroom CC catalog lives at:
```
~/Pictures/Lightroom Library.lrlibrary/<catalog-id>/Managed Catalog.mcat
```

The `<catalog-id>` is a UUID specific to each user's library (e.g., `b67ffe07bd574f4b89f1f6194ebb8d3b`). To find it:

```bash
ls ~/Pictures/Lightroom\ Library.lrlibrary/
```

There is typically one directory — that's the catalog ID.

## Prerequisites

```bash
pip install msgpack
```

## Indexing the Catalog

Use `lightroom-index.py` to build the search index. The script reads the Lightroom catalog and creates a SQLite+FTS5 database.

### Configuration

Edit these constants at the top of `lightroom-index.py` to match the user's setup:

```python
# Path to Lightroom's internal catalog database
CATALOG_PATH = os.path.expanduser(
    "~/Pictures/Lightroom Library.lrlibrary/<catalog-id>/Managed Catalog.mcat"
)

# Where original photo files live (optional, for --with-path resolution)
ORIGINALS_BASE = "/path/to/Lightroom/originals/<catalog-id>/originals"

# Where to write the search index
DB_PATH = "/path/to/lightroom.db"
```

### Running the Indexer

```bash
# Full index (first time, or to rebuild)
python3 lightroom-index.py ingest --full

# Incremental update (only new/changed revisions since last run)
python3 lightroom-index.py ingest
```

The indexer tracks its last-processed revision sequence, so incremental updates are fast.

## Searching

### CLI Search

```bash
# Full-text search (searches filenames, keywords, camera info)
python3 lightroom-index.py search "sunset"

# With filters
python3 lightroom-index.py search "portrait" --rating 4 --year 2024
python3 lightroom-index.py search "*" --camera "Sony" --lens "85mm"
python3 lightroom-index.py search "*" --edited --rating 3
python3 lightroom-index.py search "*" --date 2024-06-15
python3 lightroom-index.py search "*" --date-from 2024-01-01 --date-to 2024-03-31

# Include file paths in results
python3 lightroom-index.py search "landscape" --with-path --limit 50

# Use "*" as query to match all (filter-only mode)
python3 lightroom-index.py search "*" --rating 5
```

### Search Filters

| Flag | Description |
|------|-------------|
| `--rating N` | Minimum star rating (>=) |
| `--rating-exact N` | Exact star rating (=) |
| `--year YYYY` | Filter by capture year |
| `--edited` | Only edited photos (filename contains `-Edit.`) |
| `--camera TEXT` | Camera make or model contains text |
| `--lens TEXT` | Lens name contains text |
| `--date YYYY-MM-DD` | Exact capture date |
| `--date-from DATE` | Capture date >= (inclusive) |
| `--date-to DATE` | Capture date <= (inclusive) |
| `--limit N` | Max results (default 20) |
| `--with-path` | Include original file path in output |

### Other Commands

```bash
# Library statistics (total assets, rating distribution, top cameras, years)
python3 lightroom-index.py stats

# Top keywords in the library
python3 lightroom-index.py keywords --top 30

# Random rated photo (optionally filtered)
python3 lightroom-index.py random --rating 4 --keyword landscape
```

## Querying the Index Directly

For more complex queries, open the index database directly with SQLite:

```python
import sqlite3
conn = sqlite3.connect("/path/to/lightroom.db")
```

### Common Queries

```sql
-- Full-text search via FTS5
SELECT a.* FROM assets a
WHERE a.id IN (SELECT asset_id FROM assets_fts WHERE assets_fts MATCH 'sunset');

-- Top-rated photos from a specific year
SELECT filename, capture_date, rating, camera_model, lens
FROM assets WHERE rating >= 4 AND capture_year = 2024
ORDER BY rating DESC, capture_date DESC;

-- Photos by camera
SELECT filename, capture_date, rating
FROM assets WHERE camera_model LIKE '%A7R%'
ORDER BY capture_date DESC;

-- All keywords for a photo
SELECT k.keyword FROM keywords k WHERE k.asset_id = 'some-asset-id';

-- Photos with a specific keyword
SELECT a.filename, a.capture_date, a.rating
FROM assets a
JOIN keywords k ON a.id = k.asset_id
WHERE k.keyword = 'landscape';

-- Rating distribution
SELECT rating, COUNT(*) FROM assets GROUP BY rating ORDER BY rating;

-- Photos per year
SELECT capture_year, COUNT(*) FROM assets
WHERE capture_year IS NOT NULL GROUP BY capture_year ORDER BY capture_year;

-- Top cameras used
SELECT camera_model, COUNT(*) c FROM assets
WHERE camera_model IS NOT NULL GROUP BY camera_model ORDER BY c DESC LIMIT 10;

-- Edited vs original count
SELECT is_edited, COUNT(*) FROM assets GROUP BY is_edited;
```

## Database Schema

See `references/schema.md` for the full schema. Key tables:

| Table | Purpose |
|-------|---------|
| `assets` | Photo metadata (filename, date, rating, EXIF, dimensions, etc.) |
| `keywords` | Keyword tags per asset (many-to-many) |
| `albums` | Album hierarchy |
| `album_assets` | Album-to-asset membership |
| `assets_fts` | FTS5 virtual table for full-text search |
| `ingest_meta` | Tracks last ingest sequence for incremental updates |

### Key Asset Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | TEXT | Unique asset identifier (doc_id from catalog) |
| `filename` | TEXT | Original filename |
| `capture_date` | TEXT | `YYYY-MM-DD` format |
| `capture_year` | INT | Year extracted for fast filtering |
| `rating` | INT | Star rating (0-5) |
| `is_edited` | INT | 1 if filename contains `-Edit.` |
| `camera_make` | TEXT | e.g., `SONY`, `Canon` |
| `camera_model` | TEXT | e.g., `ILCE-7RM4` |
| `lens` | TEXT | e.g., `FE 24-70mm F2.8 GM` |
| `focal_length_35mm` | INT | 35mm equivalent focal length |
| `iso` | INT | ISO speed |
| `aperture` | REAL | f-number |
| `raw_keywords` | TEXT | JSON array of keywords |

## Reference Files

- `references/schema.md` — Full database schema with all columns and indexes
- `references/indexer.md` — The complete indexer script for reference
