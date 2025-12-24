#!/usr/bin/env python3
"""
Create a clean SQLite database with decoded iMessage messages.

Usage:
    python create_clean_db.py <source_db> <output_db> <chat_ids>

Examples:
    # Single conversation
    python create_clean_db.py ~/Library/Messages/chat.db ./messages.db 123

    # Multiple conversations
    python create_clean_db.py ~/Library/Messages/chat.db ./messages.db 123,456,789

    # Export all conversations
    python create_clean_db.py ~/Library/Messages/chat.db ./messages.db all
"""

import sqlite3
import re
import sys
import os
from datetime import datetime

# Apple epoch constant
APPLE_EPOCH = 978307200

# Try to import PyObjC for best decoding
try:
    from Foundation import NSData, NSKeyedUnarchiver
    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False
    print("Note: PyObjC not available, using fallback decoder")


def apple_to_datetime(timestamp):
    """Convert Apple nanosecond timestamp to datetime string."""
    if not timestamp:
        return None
    unix_ts = (timestamp / 1_000_000_000) + APPLE_EPOCH
    return datetime.fromtimestamp(unix_ts).strftime('%Y-%m-%d %H:%M:%S')


def apple_to_unix(timestamp):
    """Convert Apple nanosecond timestamp to Unix timestamp."""
    if not timestamp:
        return None
    return int(timestamp / 1_000_000_000 + APPLE_EPOCH)


def decode_attributed_body(data):
    """Decode NSAttributedString from attributedBody blob."""
    if not data:
        return None

    # Method 1: PyObjC
    if PYOBJC_AVAILABLE:
        try:
            ns_data = NSData.dataWithBytes_length_(data, len(data))
            unarchiver = NSKeyedUnarchiver.alloc().initForReadingWithData_(ns_data)
            unarchiver.setRequiresSecureCoding_(False)
            obj = unarchiver.decodeObjectForKey_("root")
            if obj and hasattr(obj, 'string'):
                text = str(obj.string())
                if text:
                    return text
        except:
            pass

    # Method 2: NSString marker
    if b'NSString' in data:
        idx = data.find(b'NSString') + 8
        if idx < len(data):
            end_idx = data.find(b'\x00', idx)
            if end_idx > idx:
                text = data[idx:end_idx].decode('utf-8', errors='ignore')
                if text:
                    return text

    # Method 3: Direct UTF-8
    offset = 50
    if len(data) > offset:
        potential = data[offset:].decode('utf-8', errors='ignore')
        cleaned = ''.join(c for c in potential if c.isprintable() or c in '\n\r\t')
        if cleaned:
            return cleaned.strip()

    return '[binary data]'


def clean_message(text):
    """Clean decoding artifacts from message text."""
    if not text or text in ['[binary data]', '[no text]']:
        return text

    # Object replacement character -> [image]
    text = text.replace('\ufffc', '[image]')

    # Remove non-printable chars
    text = ''.join(c for c in text if c.isprintable() or c in '\n\r\t')

    # Remove leading format codes
    text = re.sub(r'^[\+\*\!\.\,\;\#\%\`\~\^\&\@\$\s]+', '', text)

    # Remove trailing NS* artifacts
    text = re.sub(r'\s*NSDictionary\s*$', '', text)
    text = re.sub(r'\s*NSMutable[A-Za-z]+\s*$', '', text)

    # Remove trailing iMessage metadata (e.g., &__kIMBaseWritingDirection...)
    text = re.sub(r'\s*&?__kIM[^\s]*.*$', '', text)

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

    # Collapse multiple spaces
    text = re.sub(r'  +', ' ', text)

    return text.strip()


# Quote characters (ASCII and Unicode curly quotes)
QUOTE_CHARS = '"\'""\u201c\u201d\u2018\u2019'


def is_reaction_message(text):
    """Check if message is a reaction (Loved, Laughed at, etc.).

    Uses regex instead of startswith() because reaction messages use
    Unicode curly quotes (U+201C, U+201D) which vary and cause matching issues.
    Format: ReactionWord + space + curly_quote + original_message + curly_quote
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


def get_all_chat_ids(cursor):
    """Get all chat IDs from the database."""
    cursor.execute("SELECT ROWID FROM chat")
    return [row[0] for row in cursor.fetchall()]


def create_clean_database(source_db, target_db, chat_ids):
    """Create a clean database with decoded messages."""
    print(f"Source: {source_db}")
    print(f"Target: {target_db}")
    print(f"Chat IDs: {chat_ids}")
    print()

    source_conn = sqlite3.connect(source_db)
    target_conn = sqlite3.connect(target_db)

    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # Create schema
    print("Creating schema...")
    target_cursor.executescript("""
        DROP TABLE IF EXISTS messages;
        DROP TABLE IF EXISTS chats;
        DROP TABLE IF EXISTS handles;
        DROP TABLE IF EXISTS attachments;
        DROP TABLE IF EXISTS message_chat_join;
        DROP TABLE IF EXISTS chat_handle_join;
        DROP TABLE IF EXISTS message_attachment_join;

        CREATE TABLE messages (
            id INTEGER PRIMARY KEY,
            guid TEXT UNIQUE,
            text TEXT,
            decoded_text TEXT,
            date TEXT,
            date_unix INTEGER,
            is_from_me INTEGER,
            is_read INTEGER,
            is_delivered INTEGER,
            is_sent INTEGER,
            has_attachments INTEGER,
            service TEXT,
            handle_id INTEGER,
            associated_message_type INTEGER,
            is_reaction INTEGER,
            is_quote INTEGER
        );

        CREATE TABLE chats (
            id INTEGER PRIMARY KEY,
            guid TEXT UNIQUE,
            chat_identifier TEXT,
            display_name TEXT,
            service_name TEXT
        );

        CREATE TABLE handles (
            id INTEGER PRIMARY KEY,
            contact_id TEXT,
            service TEXT
        );

        CREATE TABLE attachments (
            id INTEGER PRIMARY KEY,
            guid TEXT UNIQUE,
            filename TEXT,
            mime_type TEXT,
            total_bytes INTEGER
        );

        CREATE TABLE message_chat_join (
            message_id INTEGER,
            chat_id INTEGER,
            PRIMARY KEY (message_id, chat_id)
        );

        CREATE TABLE chat_handle_join (
            chat_id INTEGER,
            handle_id INTEGER,
            PRIMARY KEY (chat_id, handle_id)
        );

        CREATE TABLE message_attachment_join (
            message_id INTEGER,
            attachment_id INTEGER,
            PRIMARY KEY (message_id, attachment_id)
        );

        CREATE INDEX idx_messages_date ON messages(date_unix);
        CREATE INDEX idx_messages_from_me ON messages(is_from_me);
        CREATE INDEX idx_messages_handle ON messages(handle_id);
    """)
    target_conn.commit()

    # Copy chats
    chat_ids_str = ','.join(map(str, chat_ids))
    source_cursor.execute(f"""
        SELECT ROWID, guid, chat_identifier, display_name, service_name
        FROM chat WHERE ROWID IN ({chat_ids_str})
    """)
    chats = source_cursor.fetchall()
    target_cursor.executemany("INSERT INTO chats VALUES (?, ?, ?, ?, ?)", chats)
    print(f"Copied {len(chats)} chats")

    # Copy handles
    source_cursor.execute(f"""
        SELECT DISTINCT h.ROWID, h.id, h.service
        FROM handle h
        JOIN message m ON m.handle_id = h.ROWID
        JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
        WHERE cmj.chat_id IN ({chat_ids_str})
    """)
    handles = source_cursor.fetchall()
    target_cursor.executemany("INSERT INTO handles VALUES (?, ?, ?)", handles)
    print(f"Copied {len(handles)} handles")

    # Process messages
    print("Processing messages...")
    source_cursor.execute(f"""
        SELECT
            m.ROWID, m.guid, m.text, m.attributedBody, m.date,
            m.is_from_me, m.is_read, m.is_delivered, m.is_sent,
            m.cache_has_attachments, m.service, m.handle_id,
            m.associated_message_type
        FROM message m
        JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
        WHERE cmj.chat_id IN ({chat_ids_str})
        ORDER BY m.date ASC
    """)

    messages = []
    count = 0
    for row in source_cursor.fetchall():
        count += 1
        if count % 10000 == 0:
            print(f"  {count:,} messages processed...")

        # Decode text
        if row[2]:
            decoded = row[2]
        elif row[3]:
            decoded = decode_attributed_body(row[3])
        else:
            decoded = ''

        cleaned = clean_message(decoded) if decoded else ''

        # Detect reaction and quote messages
        reaction = 1 if is_reaction_message(cleaned) else 0
        quote = 1 if is_quoted_message(cleaned) else 0

        messages.append((
            row[0],                          # id
            row[1],                          # guid
            row[2],                          # text
            cleaned,                         # decoded_text
            apple_to_datetime(row[4]),       # date
            apple_to_unix(row[4]),           # date_unix
            row[5], row[6], row[7], row[8],  # flags
            row[9],                          # has_attachments
            row[10],                         # service
            row[11],                         # handle_id
            row[12],                         # associated_message_type
            reaction,                        # is_reaction
            quote                            # is_quote
        ))

    target_cursor.executemany(
        "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        messages
    )
    print(f"Processed {len(messages):,} messages")

    # Copy junction tables
    source_cursor.execute(f"""
        SELECT message_id, chat_id FROM chat_message_join
        WHERE chat_id IN ({chat_ids_str})
    """)
    target_cursor.executemany("INSERT INTO message_chat_join VALUES (?, ?)",
                              source_cursor.fetchall())

    source_cursor.execute(f"""
        SELECT chat_id, handle_id FROM chat_handle_join
        WHERE chat_id IN ({chat_ids_str})
    """)
    target_cursor.executemany("INSERT INTO chat_handle_join VALUES (?, ?)",
                              source_cursor.fetchall())

    # Create readable view
    target_cursor.execute("""
        CREATE VIEW IF NOT EXISTS messages_readable AS
        SELECT
            m.id, m.guid, m.date,
            CASE WHEN m.is_from_me = 1 THEN 'You' ELSE h.contact_id END as sender,
            m.decoded_text as message,
            m.has_attachments, m.service,
            m.is_reaction, m.is_quote
        FROM messages m
        LEFT JOIN handles h ON m.handle_id = h.id
        ORDER BY m.date_unix
    """)

    # Create view excluding reactions and quotes (for analysis)
    target_cursor.execute("""
        CREATE VIEW IF NOT EXISTS messages_clean AS
        SELECT
            m.id, m.guid, m.date,
            CASE WHEN m.is_from_me = 1 THEN 'You' ELSE h.contact_id END as sender,
            m.decoded_text as message,
            m.has_attachments, m.service
        FROM messages m
        LEFT JOIN handles h ON m.handle_id = h.id
        WHERE m.is_reaction = 0 AND m.is_quote = 0
        ORDER BY m.date_unix
    """)

    target_conn.commit()
    source_conn.close()
    target_conn.close()

    print()
    print(f"Created: {target_db}")
    print(f"Messages: {len(messages):,}")
    print()
    print("Query examples:")
    print(f"  # All messages")
    print(f"  sqlite3 {target_db} \"SELECT * FROM messages_readable LIMIT 10;\"")
    print(f"  # Exclude reactions and quotes (cleaner for analysis)")
    print(f"  sqlite3 {target_db} \"SELECT * FROM messages_clean LIMIT 10;\"")
    print(f"  # Search")
    print(f"  sqlite3 {target_db} \"SELECT * FROM messages_clean WHERE message LIKE '%keyword%';\"")


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    source_db = os.path.expanduser(sys.argv[1])
    target_db = os.path.expanduser(sys.argv[2])
    chat_ids_arg = sys.argv[3]

    if not os.path.exists(source_db):
        print(f"Error: Source database not found: {source_db}")
        sys.exit(1)

    # Parse chat IDs
    conn = sqlite3.connect(source_db)
    cursor = conn.cursor()

    if chat_ids_arg.lower() == 'all':
        chat_ids = get_all_chat_ids(cursor)
    else:
        chat_ids = [int(x.strip()) for x in chat_ids_arg.split(',')]

    conn.close()

    if not chat_ids:
        print("Error: No chat IDs found")
        sys.exit(1)

    create_clean_database(source_db, target_db, chat_ids)


if __name__ == '__main__':
    main()
