# Lightroom Index Database Schema

SQLite + FTS5, WAL mode.

## Tables

### assets

Primary table storing photo metadata extracted from Lightroom's catalog.

```sql
CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,           -- doc_id from Lightroom catalog
    doc_id TEXT,                   -- same as id
    filename TEXT,                 -- original filename (e.g., DSC01234.ARW)
    file_ext TEXT,                 -- lowercase extension (e.g., arw, jpg)
    is_edited INTEGER DEFAULT 0,  -- 1 if filename contains '-Edit.'
    capture_date TEXT,             -- YYYY-MM-DD format
    capture_year INTEGER,          -- extracted year for fast filtering
    capture_month INTEGER,         -- extracted month (1-12)
    rating INTEGER DEFAULT 0,     -- star rating 0-5
    width INTEGER,                -- pixel width (cropped if available)
    height INTEGER,               -- pixel height (cropped if available)
    camera_make TEXT,             -- EXIF Make (e.g., SONY, Canon)
    camera_model TEXT,            -- EXIF Model (e.g., ILCE-7RM4)
    lens TEXT,                    -- EXIF Lens (e.g., FE 24-70mm F2.8 GM)
    focal_length_35mm INTEGER,   -- 35mm equivalent focal length
    iso INTEGER,                  -- ISO speed rating
    shutter_speed TEXT,           -- exposure time as string
    aperture REAL,                -- f-number
    content_type TEXT,            -- MIME type (e.g., image/x-sony-arw)
    file_size INTEGER,            -- bytes
    sha256 TEXT,                  -- file hash
    type TEXT,                    -- always 'asset' for photos
    subtype TEXT,                 -- asset subtype from catalog
    imported_at TEXT,             -- import timestamp
    updated_at TEXT,              -- last user update timestamp
    raw_keywords TEXT,            -- JSON array of keyword strings
    catalog_rev_sequence INTEGER, -- revision sequence from catalog
    indexed_at TEXT DEFAULT (datetime('now'))
);
```

### keywords

Normalized keyword tags, one row per asset-keyword pair.

```sql
CREATE TABLE IF NOT EXISTS keywords (
    asset_id TEXT REFERENCES assets(id),
    keyword TEXT NOT NULL,
    PRIMARY KEY (asset_id, keyword)
);
```

### albums

Album hierarchy from the catalog.

```sql
CREATE TABLE IF NOT EXISTS albums (
    id TEXT PRIMARY KEY,
    name TEXT,
    subtype TEXT,
    parent_id TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

### album_assets

Many-to-many relationship between albums and assets.

```sql
CREATE TABLE IF NOT EXISTS album_assets (
    album_id TEXT REFERENCES albums(id),
    asset_id TEXT REFERENCES assets(id),
    PRIMARY KEY (album_id, asset_id)
);
```

### ingest_meta

Key-value store tracking indexer state.

```sql
CREATE TABLE IF NOT EXISTS ingest_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

Keys used:
- `last_sequence` — highest revision sequence processed (for incremental ingest)
- `last_ingest` — ISO timestamp of last ingest run

### assets_fts (FTS5 virtual table)

Full-text search index over asset metadata.

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS assets_fts USING fts5(
    asset_id,     -- links back to assets.id
    filename,     -- searchable filename
    keywords,     -- space-separated keyword string
    camera_info   -- concatenated camera_make + camera_model + lens
);
```

Query with FTS5 MATCH syntax:
```sql
SELECT asset_id FROM assets_fts WHERE assets_fts MATCH 'sunset AND landscape';
SELECT asset_id FROM assets_fts WHERE assets_fts MATCH 'sony OR canon';
```

## Indexes

```sql
CREATE INDEX idx_assets_rating ON assets(rating);
CREATE INDEX idx_assets_capture_date ON assets(capture_date);
CREATE INDEX idx_assets_capture_year ON assets(capture_year);
CREATE INDEX idx_assets_is_edited ON assets(is_edited);
CREATE INDEX idx_keywords_keyword ON keywords(keyword);
CREATE INDEX idx_assets_type ON assets(type);
```
