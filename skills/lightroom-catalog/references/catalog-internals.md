# Lightroom CC Catalog Internals

How Adobe Lightroom CC stores photo metadata on macOS.

## File Structure

```
~/Pictures/Lightroom Library.lrlibrary/
├── <catalog-uuid>/
│   ├── Managed Catalog.mcat      ← SQLite database (the catalog)
│   └── originals/                ← Local photo files (if stored locally)
│       └── YYYY/YYYY-MM-DD/filename.ext
├── FolderSourcePreviews/
├── profiles/
├── TemporaryEdits/
└── user/
```

The `<catalog-uuid>` is a hex string unique to each catalog (e.g., `b67ffe07bd574f4b89f1f6194ebb8d3b`).

## The .mcat File

`Managed Catalog.mcat` is a standard SQLite database. Open read-only:

```python
import sqlite3
cat = sqlite3.connect("file:path/to/Managed Catalog.mcat?mode=ro", uri=True)
cat.text_factory = bytes  # required — content is binary
```

### Key Tables

| Table | Purpose |
|-------|---------|
| `docs` | Document registry — one row per logical entity (photo, album, etc.) |
| `revs` | Revision history — msgpack-encoded content for each document version |

### Querying Current State

Each document has a "winning" revision (the current version):

```sql
SELECT d.fullDocId, r.content, r.sequence
FROM docs d
JOIN revs r ON d.winningRevSequence = r.sequence
ORDER BY r.sequence
```

- `fullDocId` — UUID identifying the document
- `content` — msgpack-encoded binary blob
- `sequence` — monotonically increasing revision number (used for incremental sync)

### Incremental Sync

Track the highest `sequence` number from each ingest. On next run, query only revisions with `sequence > last_sequence`:

```sql
SELECT d.fullDocId, r.content, r.sequence
FROM docs d
JOIN revs r ON d.winningRevSequence = r.sequence
WHERE r.sequence > ?
ORDER BY r.sequence
```

## Msgpack Revision Format

Each revision's `content` is decoded with `msgpack.unpackb(content, raw=False)`.

### Document Types

The `type` field determines what the document represents:

| Type | Description |
|------|-------------|
| `asset` | A photo or video |
| `album` | An album or collection |
| Other | Internal Lightroom state (ignored) |

### Asset Fields

```python
{
    "type": "asset",
    "subtype": "image",
    "importSource": {
        "fileName": "DSC_1234.NEF",
        "originalName": "DSC_1234.NEF"
    },
    "captureDate": "2024-06-15T14:30:00",
    "ratings": {
        "<device-uuid>": {"rating": 4, ...}
    },
    "width": 6000,
    "height": 4000,
    "croppedWidth": 5800,    # after crop
    "croppedHeight": 3900,
    "contentType": "image/x-nikon-nef",
    "fileSize": 28456789,
    "sha256": "abc123...",
    "importTimestamp": "2024-06-15T16:00:00",
    "userUpdated": "2024-06-16T10:00:00",
    "xmp": {
        "tiff": {
            "Make": "NIKON CORPORATION",
            "Model": "NIKON Z 6_2"
        },
        "exif": {
            "ISOSpeedRatings": [800],
            "ExposureTime": "1/250",
            "FNumber": 2.8,
            "FocalLengthIn35mmFilm": 85
        },
        "aux": {
            "Lens": "NIKKOR Z 85mm f/1.8 S"
        },
        "dc": {
            "subject": {"landscape": true, "sunset": true}
            # or: ["landscape", "sunset"]
        }
    }
}
```

### Ratings

Ratings are per-device. Structure: `{"<device-uuid>": {"rating": N}}`. Take the max across devices. Rating values are 0-5 stars.

### Keywords

Keywords live at `xmp.dc.subject`. Can be either:
- A **dict** with keyword names as keys and truthy values: `{"sunset": true, "beach": true}`
- A **list** of strings: `["sunset", "beach"]`

### EXIF Gotchas

Some EXIF fields return as single-element lists instead of scalars:
- `ISOSpeedRatings`: `[800]` not `800`
- `FNumber`: sometimes `[2.8]`
- `ExposureTime`: sometimes `["1/250"]`
- `FocalLengthIn35mmFilm`: sometimes `[85]`

Always unwrap lists by taking the first element.

## Originals Path Layout

When photos are stored locally (or synced to an external drive), the directory structure is:

```
originals/
└── YYYY/
    └── YYYY-MM-DD/
        └── filename.ext
```

To resolve a file path from asset metadata:
```python
year = capture_date[:4]
date_dir = capture_date[:10]  # YYYY-MM-DD
path = f"{originals_base}/{year}/{date_dir}/{filename}"
```

## Edited Photos

Lightroom creates separate files for edits with `-Edit.` in the filename:
- Original: `DSC_1234.NEF`
- Edit: `DSC_1234-Edit.jpg`

Both appear as separate assets in the catalog.
