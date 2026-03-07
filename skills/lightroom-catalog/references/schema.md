# Output Database Schema

The indexer creates a SQLite database with FTS5 full-text search.

## Tables

### `assets` — Photo metadata

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Document UUID from catalog |
| `doc_id` | TEXT | Same as id (catalog document ID) |
| `filename` | TEXT | Original filename (e.g., `DSC_1234.NEF`) |
| `file_ext` | TEXT | Lowercase extension (e.g., `nef`) |
| `is_edited` | INTEGER | 1 if filename contains `-Edit.` |
| `capture_date` | TEXT | `YYYY-MM-DD` format |
| `capture_year` | INTEGER | Year extracted from capture_date |
| `capture_month` | INTEGER | Month (1-12) |
| `rating` | INTEGER | Star rating 0-5 (max across devices) |
| `width` | INTEGER | Cropped width (or original if uncropped) |
| `height` | INTEGER | Cropped height |
| `camera_make` | TEXT | e.g., `NIKON CORPORATION` |
| `camera_model` | TEXT | e.g., `NIKON Z 6_2` |
| `lens` | TEXT | e.g., `NIKKOR Z 85mm f/1.8 S` |
| `focal_length_35mm` | INTEGER | 35mm equivalent focal length |
| `iso` | INTEGER | ISO sensitivity |
| `shutter_speed` | TEXT | e.g., `1/250` |
| `aperture` | REAL | f-number (e.g., `2.8`) |
| `content_type` | TEXT | MIME type (e.g., `image/jpeg`) |
| `file_size` | INTEGER | Bytes |
| `sha256` | TEXT | File hash |
| `type` | TEXT | Always `asset` |
| `subtype` | TEXT | e.g., `image`, `video` |
| `imported_at` | TEXT | Import timestamp |
| `updated_at` | TEXT | Last user edit timestamp |
| `raw_keywords` | TEXT | JSON array of keywords |
| `catalog_rev_sequence` | INTEGER | Catalog revision number |
| `indexed_at` | TEXT | When this row was written |

### `keywords` — Asset-keyword junction

| Column | Type | Description |
|--------|------|-------------|
| `asset_id` | TEXT | FK to assets.id |
| `keyword` | TEXT | Keyword string |

Primary key: `(asset_id, keyword)`

### `albums`

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT PK | Album UUID |
| `name` | TEXT | Album name |
| `subtype` | TEXT | Album type |
| `parent_id` | TEXT | Parent album UUID |
| `created_at` | TEXT | Creation timestamp |
| `updated_at` | TEXT | Last update timestamp |

### `album_assets` — Album membership

| Column | Type | Description |
|--------|------|-------------|
| `album_id` | TEXT | FK to albums.id |
| `asset_id` | TEXT | FK to assets.id |

### `ingest_meta` — Sync state

| Column | Type | Description |
|--------|------|-------------|
| `key` | TEXT PK | `last_sequence` or `last_ingest` |
| `value` | TEXT | Sequence number or ISO timestamp |

### `assets_fts` — Full-text search (FTS5)

| Column | Description |
|--------|-------------|
| `asset_id` | Document UUID |
| `filename` | Searchable filename |
| `keywords` | Space-separated keywords |
| `camera_info` | Make + model + lens concatenated |

## Indexes

- `idx_assets_rating` — rating
- `idx_assets_capture_date` — capture_date
- `idx_assets_capture_year` — capture_year
- `idx_assets_is_edited` — is_edited
- `idx_keywords_keyword` — keyword
- `idx_assets_type` — type

## Example Queries

**All 5-star photos from 2024:**
```sql
SELECT filename, capture_date, camera_model, lens
FROM assets
WHERE rating = 5 AND capture_year = 2024
ORDER BY capture_date DESC;
```

**Full-text search with FTS5:**
```sql
SELECT a.filename, a.capture_date, a.rating
FROM assets a
WHERE a.id IN (
    SELECT asset_id FROM assets_fts WHERE assets_fts MATCH 'sunset'
)
ORDER BY a.rating DESC;
```

**Photos by camera and date range:**
```sql
SELECT filename, capture_date, rating, iso, aperture, shutter_speed
FROM assets
WHERE camera_model LIKE '%Z 6%'
  AND capture_date BETWEEN '2024-06-01' AND '2024-06-30'
ORDER BY capture_date;
```

**Keyword frequency:**
```sql
SELECT keyword, COUNT(*) as cnt
FROM keywords
GROUP BY keyword
ORDER BY cnt DESC
LIMIT 20;
```

**Photos shot at wide apertures:**
```sql
SELECT filename, capture_date, aperture, lens, rating
FROM assets
WHERE aperture <= 2.0 AND rating >= 3
ORDER BY rating DESC, capture_date DESC;
```
