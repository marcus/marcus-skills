---
name: lightroom-catalog
description: Index and search Adobe Lightroom CC catalogs on macOS. Build a searchable SQLite+FTS5 database from the .mcat catalog, with incremental sync, full-text search, EXIF/keyword filtering, and stats. Use when user wants to query their Lightroom library, find photos by metadata, or set up automated catalog indexing.
---

# Lightroom Catalog Index

Build a searchable SQLite+FTS5 index from Adobe Lightroom CC's internal catalog on macOS. Extracts photo metadata (EXIF, ratings, keywords, dimensions, camera info) into a clean, queryable database.

## Prerequisites

- macOS with Adobe Lightroom CC installed
- Python 3.8+
- `pip install msgpack`

## Quick Start

### 1. Find the catalog

Lightroom CC stores its catalog at:
```
~/Pictures/Lightroom Library.lrlibrary/*/Managed Catalog.mcat
```

The script auto-detects this. To verify:
```bash
ls ~/Pictures/*.lrlibrary/*/Managed\ Catalog.mcat
```

### 2. Run initial ingest

```bash
python3 scripts/lightroom-index.py ingest --full
```

This creates `./lightroom.db` with all photo metadata. A 200K+ photo library takes about 2 minutes.

### 3. Search

```bash
python3 scripts/lightroom-index.py search "sunset"
python3 scripts/lightroom-index.py search "*" --rating 4 --year 2024
python3 scripts/lightroom-index.py stats
```

## Configuration

Three ways to configure paths (in order of precedence):

| Method | Catalog | Database | Originals |
|--------|---------|----------|-----------|
| CLI flags | `--catalog PATH` | `--db PATH` | `--originals PATH` |
| Env vars | `LIGHTROOM_CATALOG` | `LIGHTROOM_DB` | `LIGHTROOM_ORIGINALS` |
| Auto-detect | `~/Pictures/*.lrlibrary` | `./lightroom.db` | — |

## CLI Reference

### `ingest` — Index the catalog

```bash
lightroom-index.py ingest [--full]
```

- Default: incremental (only new/changed photos since last run)
- `--full`: rebuild from scratch
- Output: JSON with `assets_indexed`, `total_revisions`, `errors`, `max_sequence`

### `search` — Find photos

```bash
lightroom-index.py search <query> [filters]
```

| Filter | Description |
|--------|-------------|
| `--rating N` | Minimum star rating |
| `--rating-exact N` | Exact star rating |
| `--year YYYY` | Capture year |
| `--edited` | Only edited photos |
| `--camera TEXT` | Camera model/make substring |
| `--lens TEXT` | Lens name substring |
| `--date YYYY-MM-DD` | Exact capture date |
| `--date-from` / `--date-to` | Date range (inclusive) |
| `--limit N` | Max results (default: 20) |
| `--with-path` | Include file paths (needs `--originals`) |

Use `"*"` as query to match all photos (filter-only mode).

### `stats` — Library overview

Returns total assets, rated/edited/keyword counts, rating distribution, top cameras, year distribution.

### `keywords` — Top keywords

```bash
lightroom-index.py keywords [--top N]
```

### `random` — Random rated photo

```bash
lightroom-index.py random [--rating N] [--keyword TEXT]
```

## Automated Scheduling (LaunchAgent)

To run incremental ingest nightly, create `~/Library/LaunchAgents/com.lightroom.indexer.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lightroom.indexer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/lightroom-index.py</string>
        <string>ingest</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>LIGHTROOM_DB</key>
        <string>/path/to/lightroom.db</string>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>1</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/lightroom-index.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/lightroom-index.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.lightroom.indexer.plist
```

Verify:
```bash
launchctl list | grep lightroom
```

## Reference Files

- [references/catalog-internals.md](references/catalog-internals.md) — How Adobe Lightroom CC stores data in .mcat
- [references/schema.md](references/schema.md) — Output SQLite database schema
- [scripts/lightroom-index.py](scripts/lightroom-index.py) — The indexer script
