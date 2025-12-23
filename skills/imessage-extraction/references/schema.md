# iMessage Database Schema Reference

Location: `~/Library/Messages/chat.db`

## Core Tables

### message

Primary table for all messages.

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | Primary key |
| guid | TEXT | Unique message identifier |
| text | TEXT | Plain text content (often NULL) |
| attributedBody | BLOB | NSAttributedString content (see decoding.md) |
| date | INTEGER | Apple timestamp (nanoseconds since 2001-01-01) |
| date_read | INTEGER | When message was read |
| date_delivered | INTEGER | When message was delivered |
| is_from_me | INTEGER | 1 = sent by user, 0 = received |
| is_read | INTEGER | Read status |
| is_delivered | INTEGER | Delivery status |
| is_sent | INTEGER | Send status |
| is_audio_message | INTEGER | Audio message flag |
| cache_has_attachments | INTEGER | Has attachments flag |
| cache_roomnames | TEXT | Group chat room name |
| service | TEXT | 'iMessage' or 'SMS' |
| account | TEXT | Account identifier |
| handle_id | INTEGER | FK to handle.ROWID |
| associated_message_type | INTEGER | Reaction/reply type |
| associated_message_guid | TEXT | GUID of associated message |
| reply_to_guid | TEXT | GUID of message being replied to |
| thread_originator_guid | TEXT | Thread starter GUID |
| thread_originator_part | TEXT | Thread part info |

### chat

Conversation/group information.

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | Primary key (chat_id) |
| guid | TEXT | Unique chat identifier |
| chat_identifier | TEXT | Phone/email/group identifier |
| display_name | TEXT | User-set display name |
| service_name | TEXT | Service type |
| style | INTEGER | Chat style (45=individual, 43=group) |
| state | INTEGER | Chat state |
| account_id | TEXT | Account identifier |

### handle

Contacts/participants.

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | Primary key |
| id | TEXT | Phone number or email |
| service | TEXT | Service type |
| country | TEXT | Country code |
| uncanonicalized_id | TEXT | Raw identifier |

### attachment

Media and file attachments.

| Column | Type | Description |
|--------|------|-------------|
| ROWID | INTEGER | Primary key |
| guid | TEXT | Unique attachment identifier |
| filename | TEXT | Full file path |
| mime_type | TEXT | MIME type |
| transfer_name | TEXT | Display filename |
| total_bytes | INTEGER | File size |
| is_outgoing | INTEGER | Sent/received flag |
| created_date | INTEGER | Apple timestamp |
| start_date | INTEGER | Transfer start time |
| transfer_state | INTEGER | Transfer status |
| uti | TEXT | Uniform Type Identifier |

## Junction Tables

### chat_message_join

Links messages to conversations.

| Column | Type | Description |
|--------|------|-------------|
| chat_id | INTEGER | FK to chat.ROWID |
| message_id | INTEGER | FK to message.ROWID |
| message_date | INTEGER | Message timestamp |

### chat_handle_join

Links handles to conversations.

| Column | Type | Description |
|--------|------|-------------|
| chat_id | INTEGER | FK to chat.ROWID |
| handle_id | INTEGER | FK to handle.ROWID |

### message_attachment_join

Links attachments to messages.

| Column | Type | Description |
|--------|------|-------------|
| message_id | INTEGER | FK to message.ROWID |
| attachment_id | INTEGER | FK to attachment.ROWID |

## Common Queries

### List all conversations with message counts

```sql
SELECT
    c.ROWID as chat_id,
    c.chat_identifier,
    c.display_name,
    COUNT(cmj.message_id) as message_count,
    MIN(datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime')) as first_msg,
    MAX(datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime')) as last_msg
FROM chat c
LEFT JOIN chat_message_join cmj ON c.ROWID = cmj.chat_id
LEFT JOIN message m ON cmj.message_id = m.ROWID
GROUP BY c.ROWID
ORDER BY message_count DESC;
```

### Get messages from a specific conversation

```sql
SELECT
    m.ROWID,
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    m.is_from_me,
    m.text,
    m.attributedBody,
    h.id as sender_id,
    m.cache_has_attachments
FROM message m
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
LEFT JOIN handle h ON m.handle_id = h.ROWID
WHERE cmj.chat_id = ?
ORDER BY m.date ASC;
```

### Find conversation by phone number or email

```sql
SELECT c.ROWID, c.chat_identifier, c.display_name
FROM chat c
WHERE c.chat_identifier LIKE '%5551234567%'
   OR c.chat_identifier LIKE '%email@example.com%';
```

### Get participants in a group chat

```sql
SELECT h.id, h.service
FROM handle h
JOIN chat_handle_join chj ON h.ROWID = chj.handle_id
WHERE chj.chat_id = ?;
```

### Get attachments for a message

```sql
SELECT
    a.filename,
    a.mime_type,
    a.total_bytes,
    datetime(a.created_date/1000000000 + 978307200, 'unixepoch', 'localtime') as date
FROM attachment a
JOIN message_attachment_join maj ON a.ROWID = maj.attachment_id
WHERE maj.message_id = ?;
```

### Statistics for a conversation

```sql
SELECT
    COUNT(*) as total_messages,
    SUM(CASE WHEN m.is_from_me = 1 THEN 1 ELSE 0 END) as sent,
    SUM(CASE WHEN m.is_from_me = 0 THEN 1 ELSE 0 END) as received,
    SUM(m.cache_has_attachments) as with_attachments,
    MIN(datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime')) as first_msg,
    MAX(datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime')) as last_msg
FROM message m
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
WHERE cmj.chat_id = ?;
```

### Search across all messages

```sql
SELECT
    c.chat_identifier,
    datetime(m.date/1000000000 + 978307200, 'unixepoch', 'localtime') as date,
    m.is_from_me,
    m.text
FROM message m
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
JOIN chat c ON cmj.chat_id = c.ROWID
WHERE m.text LIKE '%search term%'
ORDER BY m.date DESC
LIMIT 100;
```

### Messages by date range

```sql
-- Convert dates to Apple timestamp for filtering
-- Formula: (unix_timestamp - 978307200) * 1000000000

SELECT *
FROM message m
JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
WHERE cmj.chat_id = ?
  AND m.date >= (strftime('%s', '2023-01-01') - 978307200) * 1000000000
  AND m.date < (strftime('%s', '2024-01-01') - 978307200) * 1000000000
ORDER BY m.date;
```

## Message Types

### associated_message_type values

| Value | Meaning |
|-------|---------|
| 0 | Normal message |
| 2000 | Love reaction |
| 2001 | Like reaction |
| 2002 | Dislike reaction |
| 2003 | Laugh reaction |
| 2004 | Emphasis reaction |
| 2005 | Question reaction |
| 3000 | Remove love |
| 3001 | Remove like |
| 3002 | Remove dislike |
| 3003 | Remove laugh |
| 3004 | Remove emphasis |
| 3005 | Remove question |

### service values

| Value | Meaning |
|-------|---------|
| iMessage | Apple iMessage |
| SMS | Standard SMS/MMS |

## Notes

- **ROWID is the primary key** for all tables, not `id`
- **Timestamps are nanoseconds** since 2001-01-01 00:00:00 UTC
- **text field is often NULL** - check attributedBody for actual content
- **Group chats** have multiple entries in chat_handle_join
- **Reactions** are stored as separate messages with associated_message_type > 0
