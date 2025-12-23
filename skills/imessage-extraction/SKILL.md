---
name: imessage-extraction
description: Extract, decode, and query iMessage conversations from macOS chat.db. Use when user needs to access iMessage history, export conversations, search messages, decode attributedBody fields, convert Apple timestamps, or create clean SQLite databases from iMessage data. Handles NSKeyedArchiver decoding, artifact cleanup, and schema navigation.
---

# iMessage Extraction

Extract and process iMessage conversations from the macOS Messages database.

## Database Location

```
~/Library/Messages/chat.db
```

**Full Disk Access required**: Grant Full Disk Access to Terminal in System Preferences > Security & Privacy > Privacy > Full Disk Access.

## Quick Start

### 1. List All Conversations

```python
import sqlite3
import os

conn = sqlite3.connect(os.path.expanduser('~/Library/Messages/chat.db'))
cursor = conn.cursor()

cursor.execute("""
    SELECT c.ROWID, c.chat_identifier, c.display_name,
           COUNT(cmj.message_id) as message_count
    FROM chat c
    LEFT JOIN chat_message_join cmj ON c.ROWID = cmj.chat_id
    GROUP BY c.ROWID
    ORDER BY message_count DESC
""")

for row in cursor.fetchall():
    print(f"Chat {row[0]}: {row[1]} ({row[2] or 'No name'}) - {row[3]} messages")
```

### 2. Extract Messages from a Conversation

```python
chat_id = 123  # Replace with actual chat ID

cursor.execute("""
    SELECT m.ROWID, m.date, m.is_from_me, m.text, m.attributedBody,
           h.id as sender
    FROM message m
    JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
    LEFT JOIN handle h ON m.handle_id = h.ROWID
    WHERE cmj.chat_id = ?
    ORDER BY m.date ASC
""", (chat_id,))
```

## Apple Timestamp Conversion

iMessage uses Apple's Core Data timestamp: **nanoseconds since 2001-01-01**.

```python
from datetime import datetime

APPLE_EPOCH = 978307200  # Unix timestamp of 2001-01-01

def apple_to_datetime(apple_ns):
    """Convert Apple nanosecond timestamp to datetime."""
    if not apple_ns:
        return None
    unix_ts = (apple_ns / 1_000_000_000) + APPLE_EPOCH
    return datetime.fromtimestamp(unix_ts)

def apple_to_unix(apple_ns):
    """Convert Apple nanosecond timestamp to Unix timestamp."""
    return int(apple_ns / 1_000_000_000 + APPLE_EPOCH) if apple_ns else None

def datetime_to_apple(dt):
    """Convert datetime to Apple nanosecond timestamp."""
    unix_ts = dt.timestamp()
    return int((unix_ts - APPLE_EPOCH) * 1_000_000_000)
```

**SQL conversion**:
```sql
datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as readable_date
```

## Decoding attributedBody

Many messages store content in `attributedBody` (NSKeyedArchiver format) rather than `text`. See `references/decoding.md` for the full decoder.

**Quick decode with PyObjC** (if installed):
```python
from Foundation import NSData, NSKeyedUnarchiver

def decode_attributed_body(data):
    if not data:
        return None
    try:
        ns_data = NSData.dataWithBytes_length_(data, len(data))
        unarchiver = NSKeyedUnarchiver.alloc().initForReadingWithData_(ns_data)
        unarchiver.setRequiresSecureCoding_(False)
        obj = unarchiver.decodeObjectForKey_("root")
        return str(obj.string()) if obj and hasattr(obj, 'string') else None
    except:
        return None
```

**Install PyObjC**: `pip install pyobjc-framework-Cocoa`

**Fallback without PyObjC**: See `references/decoding.md` for manual binary parsing.

## Cleaning Message Artifacts

Decoded messages often contain artifacts:

```python
import re

def clean_message(text):
    if not text:
        return text

    # Replace object replacement character (marks images)
    text = text.replace('\ufffc', '[image]')

    # Remove non-printable characters
    text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')

    # Remove leading format codes
    text = re.sub(r'^[\+\*\!\.\,\;\#\%\`\~\^\&\@\$\s]+', '', text)

    # Remove trailing NSDictionary artifacts
    text = re.sub(r'\s*NSDictionary\s*$', '', text)
    text = re.sub(r'\s*NSMutable[A-Za-z]+\s*$', '', text)

    # Remove trailing iMessage metadata
    text = re.sub(r'[ij]I[^\s]*$', '', text)

    # Remove leading digit artifact
    text = re.sub(r'^[0-9](?=[a-zA-Z])', '', text)

    return text.strip()
```

## Creating a Clean Database

For easier querying, create a new database with decoded messages. Run `scripts/create_clean_db.py` or use this schema:

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    guid TEXT UNIQUE,
    text TEXT,
    decoded_text TEXT,
    date TEXT,
    date_unix INTEGER,
    is_from_me INTEGER,
    handle_id INTEGER,
    has_attachments INTEGER,
    service TEXT
);

CREATE TABLE handles (
    id INTEGER PRIMARY KEY,
    contact_id TEXT,
    service TEXT
);

CREATE VIEW messages_readable AS
SELECT
    m.id, m.guid, m.date,
    CASE WHEN m.is_from_me = 1 THEN 'You' ELSE h.contact_id END as sender,
    m.decoded_text as message,
    m.has_attachments
FROM messages m
LEFT JOIN handles h ON m.handle_id = h.id
ORDER BY m.date_unix;
```

## Common Queries

**Search messages:**
```sql
SELECT * FROM messages_readable WHERE message LIKE '%keyword%';
```

**Messages by date range:**
```sql
SELECT * FROM messages_readable
WHERE date BETWEEN '2023-01-01' AND '2023-12-31';
```

**Count by sender:**
```sql
SELECT sender, COUNT(*) FROM messages_readable GROUP BY sender;
```

**Messages with attachments:**
```sql
SELECT m.*, a.filename, a.mime_type
FROM message m
JOIN message_attachment_join maj ON m.ROWID = maj.message_id
JOIN attachment a ON maj.attachment_id = a.ROWID;
```

## Workflow Summary

1. **Find chat ID**: Query `chat` table to find conversation
2. **Extract messages**: Join `message` + `chat_message_join` + `handle`
3. **Decode text**: Check `text` first, then decode `attributedBody`
4. **Clean artifacts**: Apply cleaning patterns
5. **Convert timestamps**: Apply Apple epoch conversion
6. **Export**: Save to CSV, new SQLite, or other format

## Reference Files

- `references/decoding.md` - Full attributedBody decoder with fallback methods
- `references/schema.md` - Complete chat.db schema reference
- `scripts/create_clean_db.py` - Create queryable clean database
