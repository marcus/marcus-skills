---
name: imessage-extraction
description: Extract, decode, and query iMessage conversations from macOS chat.db. Use when user needs to access iMessage history, export conversations, search messages, decode attributedBody fields, convert Apple timestamps, transcribe voice messages, or create clean SQLite databases from iMessage data. Handles NSKeyedArchiver decoding, artifact cleanup, schema navigation, contact name resolution via AddressBook databases, and voice message transcription via yap.
---

# iMessage Extraction

Extract and process iMessage conversations from the macOS Messages database.

## Database Location

```
~/Library/Messages/chat.db
```

**Full Disk Access required**: Grant Full Disk Access to Terminal in System Preferences > Security & Privacy > Privacy > Full Disk Access.

**Setup steps:**
1. Go to **System Preferences > Security & Privacy > Privacy > Full Disk Access**
2. Click the `+` button and add `/Applications/Utilities/Terminal.app` (or your terminal app)
3. Restart Terminal for changes to take effect
4. Test by running: `sqlite3 ~/Library/Messages/chat.db "SELECT COUNT(*) FROM chat;"`

## Contact Resolution

macOS stores contacts in AddressBook SQLite databases. The main database at `~/Library/Application Support/AddressBook/AddressBook-v22.abcddb` is often sparse — the real data lives in per-source databases under the `Sources/` directory (iCloud, Google, Exchange, etc.).

**Database locations:**
```
~/Library/Application Support/AddressBook/AddressBook-v22.abcddb          # aggregate (often sparse)
~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb  # per-source (actual data)
```

**When the user references a contact by name** (e.g., "messages to Bonnie"), resolve the name to a phone number or email first, then use that identifier to find the chat in `chat.db`.

### Step 1: Find a contact's phone number or email

```sql
-- Run this against EACH database in Sources/*/AddressBook-v22.abcddb
SELECT r.ZFIRSTNAME, r.ZLASTNAME, p.ZFULLNUMBER, p.ZLABEL
FROM ZABCDRECORD r
JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
WHERE LOWER(r.ZFIRSTNAME) LIKE '%bonnie%';

-- For email addresses:
SELECT r.ZFIRSTNAME, r.ZLASTNAME, e.ZADDRESS
FROM ZABCDRECORD r
JOIN ZABCDEMAILADDRESS e ON e.ZOWNER = r.Z_PK
WHERE LOWER(r.ZFIRSTNAME) LIKE '%bonnie%';
```

**Shell one-liner to search all sources:**
```bash
for db in ~/Library/Application\ Support/AddressBook/Sources/*/AddressBook-v22.abcddb; do
    sqlite3 "$db" "
    SELECT r.ZFIRSTNAME, r.ZLASTNAME, p.ZFULLNUMBER
    FROM ZABCDRECORD r
    JOIN ZABCDPHONENUMBER p ON p.ZOWNER = r.Z_PK
    WHERE LOWER(r.ZFIRSTNAME) LIKE '%SEARCH_NAME%';
    " 2>/dev/null
done
```

### Step 2: Match the phone/email to a chat

Strip formatting and match the last 10 digits of the phone number against `chat.chat_identifier`:

```sql
-- Phone number (use last 10 digits to handle +1 prefix variations)
SELECT ROWID, chat_identifier, display_name
FROM chat
WHERE chat_identifier LIKE '%2087617226%';

-- Email
SELECT ROWID, chat_identifier, display_name
FROM chat
WHERE chat_identifier LIKE '%someone@email.com%';
```

### Step 3: Query that chat's messages

```sql
SELECT m.ROWID, datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
       m.is_from_me, m.text
FROM message m
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
WHERE cmj.chat_id = ?
ORDER BY m.date DESC;
```

### Key AddressBook tables

| Table | Purpose |
|---|---|
| `ZABCDRECORD` | Contact records (`ZFIRSTNAME`, `ZLASTNAME`, `ZORGANIZATION`) |
| `ZABCDPHONENUMBER` | Phone numbers (`ZFULLNUMBER`, `ZLABEL`, `ZOWNER` → record `Z_PK`) |
| `ZABCDEMAILADDRESS` | Emails (`ZADDRESS`, `ZOWNER` → record `Z_PK`) |

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

Decoded messages often contain artifacts from the typedstream encoding:

```python
import re

def clean_message(text):
    """Clean decoding artifacts from message text."""
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

    # Remove trailing iMessage metadata (e.g., &__kIMBaseWritingDirection...)
    text = re.sub(r'\s*&?__kIM[^\s]*.*$', '', text)

    # Remove trailing iMessage metadata
    text = re.sub(r'[ij]I[^\s]*$', '', text)

    # Remove leading digit artifact
    text = re.sub(r'^[0-9](?=[a-zA-Z])', '', text)

    # Remove leading single-letter artifacts from iMessage encoding
    # Patterns: "dOMG" -> "OMG", "Ohttps://" -> "https://", "Ci believe" -> "i believe"
    # BUT NOT: "OMG" -> "MG" (uppercase + uppercase = real word)
    if len(text) > 2 and text[0].isalpha():
        second_char = text[1]
        rest = text[1:]
        # Case 1: lowercase followed by uppercase (e.g., "dOMG")
        if text[0].islower() and second_char.isupper():
            text = rest
        # Case 2: any letter followed by "http" (e.g., "Ohttps://")
        elif rest[:4].lower() == 'http':
            text = rest
        # Case 3: any letter followed by "i " or "i'" (e.g., "Ci believe")
        elif second_char == 'i' and len(text) > 2 and text[2] in " '":
            text = rest

    return text.strip()
```

## Detecting Reactions and Quotes

iMessage reactions (tapbacks) and quoted messages require special handling.

**Reaction format**: `ReactionWord + space + curly_quote + original_message + curly_quote`
- Example: `Loved "When I first heard this song..."`
- Uses Unicode curly quotes: `"` (U+201C) and `"` (U+201D), not straight quotes

**Important**: Use regex matching, not `startswith()`. The curly quotes vary and cause issues with string prefix matching.

```python
# Quote characters (ASCII and Unicode curly quotes)
QUOTE_CHARS = '"\'""\u201c\u201d\u2018\u2019'

def is_reaction_message(text):
    """Check if message is a reaction (Loved, Laughed at, etc.).

    Uses regex instead of startswith() because reaction messages use
    Unicode curly quotes (U+201C, U+201D) which vary and cause matching issues.
    """
    if not text:
        return False
    return bool(re.match(r'^(Reacted|Loved|Laughed|Emphasized|Disliked|Questioned|Liked)\s', text))

def is_quoted_message(text):
    """Check if message ends with a quote (usually quoting someone)."""
    if not text:
        return False
    stripped = text.rstrip()
    return stripped[-1] in QUOTE_CHARS if stripped else False
```

Use these to filter analysis:
```python
# Skip reactions and quotes when analyzing conversation flow
meaningful_messages = [
    m for m in messages
    if not is_reaction_message(m['text']) and not is_quoted_message(m['text'])
]
```

## Voice Message Transcription

Voice messages are stored as `.caf` files in `~/Library/Messages/Attachments/`. macOS does **not** store transcriptions in the database — you must transcribe the audio at query time.

### Finding voice messages

```sql
SELECT m.ROWID, datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
       m.is_from_me, a.filename, a.total_bytes, h.id as handle
FROM message m
JOIN message_attachment_join maj ON m.ROWID = maj.message_id
JOIN attachment a ON maj.attachment_id = a.ROWID
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE m.is_audio_message = 1
ORDER BY m.date DESC;
```

To filter by chat (e.g., a specific contact):
```sql
-- Add these joins:
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
JOIN chat c ON cmj.chat_id = c.ROWID
WHERE m.is_audio_message = 1 AND c.chat_identifier LIKE '%PHONE_NUMBER%'
```

### Transcribing with yap

Use `yap` (installed via Homebrew) which wraps Apple's `SFSpeechRecognizer` for on-device transcription:

```bash
# Basic transcription to stdout
yap transcribe ~/Library/Messages/Attachments/.../Audio\ Message.caf --txt

# With JSON output (includes timestamps)
yap transcribe "path/to/Audio Message.caf" --json

# Save to file
yap transcribe "path/to/Audio Message.caf" --txt -o transcript.txt
```

**Note**: The `filename` column from the attachment table uses `~` for the home directory. Expand it before passing to `yap`:
```bash
# In shell: replace ~ with $HOME
filepath="${filename/#\~/$HOME}"
yap transcribe "$filepath" --txt
```

### Searching voice message content

Since transcriptions aren't stored, searching voice messages requires a two-step process:

1. **Query for voice messages** in the target chat (by date range, contact, etc.)
2. **Transcribe each** with `yap` and search the output

For bulk searching, transcribe to files and grep:
```bash
# Transcribe all voice messages from a chat, named by message ID
sqlite3 ~/Library/Messages/chat.db "
SELECT m.ROWID, REPLACE(a.filename, '~', '$HOME')
FROM message m
JOIN message_attachment_join maj ON m.ROWID = maj.message_id
JOIN attachment a ON maj.attachment_id = a.ROWID
WHERE m.is_audio_message = 1;
" | while IFS='|' read -r id filepath; do
    yap transcribe "$filepath" --txt -o "/tmp/voice_msg_${id}.txt" 2>/dev/null
done

# Then search
grep -rl "keyword" /tmp/voice_msg_*.txt
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

1. **Resolve contact** (if searching by name): Search AddressBook `Sources/*/AddressBook-v22.abcddb` for phone/email, then match to `chat.chat_identifier`
2. **Find chat ID**: Query `chat` table to find conversation
3. **Extract messages**: Join `message` + `chat_message_join` + `handle`
4. **Decode text**: Check `text` first, then decode `attributedBody`
5. **Transcribe voice messages** (if relevant): Use `yap transcribe` on `.caf` attachments where `is_audio_message = 1`
6. **Clean artifacts**: Apply cleaning patterns
7. **Convert timestamps**: Apply Apple epoch conversion
8. **Export**: Save to CSV, new SQLite, or other format

## Reference Files

- `references/decoding.md` - Full attributedBody decoder with fallback methods
- `references/schema.md` - Complete chat.db schema reference
- `scripts/create_clean_db.py` - Create queryable clean database
