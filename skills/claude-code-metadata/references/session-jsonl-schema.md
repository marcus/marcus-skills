# Session JSONL Complete Schema Reference

## Overview

Session files are stored in `~/.claude/projects/<encoded-path>/<session-id>.jsonl`. Each line is a complete JSON object.

## Message Threading

Messages form a linked tree via `parentUuid`:
- `parentUuid: null` = root message
- Follow chain to reconstruct conversation

`isSidechain: true` indicates a branched alternative response path.

## Complete Field Reference

### Common Fields (All Messages)

| Field | Type | Description |
|-------|------|-------------|
| `parentUuid` | string/null | UUID of parent message |
| `isSidechain` | boolean | True if alternate branch |
| `userType` | string | Always "external" |
| `cwd` | string | Working directory path |
| `sessionId` | string | Session UUID |
| `version` | string | Claude Code version |
| `gitBranch` | string | Current git branch |
| `type` | string | "user", "assistant", or "summary" |
| `uuid` | string | This message's UUID |
| `timestamp` | string | ISO 8601 timestamp |

### User Message Fields

| Field | Type | Description |
|-------|------|-------------|
| `message.role` | string | Always "user" |
| `message.content` | string/array | Message content |
| `isMeta` | boolean | True for meta/system messages |

### Assistant Message Fields

| Field | Type | Description |
|-------|------|-------------|
| `slug` | string | Human-readable session name |
| `requestId` | string | API request ID |
| `message.model` | string | Model identifier |
| `message.id` | string | API message ID |
| `message.type` | string | Always "message" |
| `message.role` | string | Always "assistant" |
| `message.content` | array | Content blocks |
| `message.stop_reason` | string/null | "end_turn", "tool_use", etc. |
| `message.stop_sequence` | string/null | Stop sequence if triggered |
| `message.usage` | object | Token usage details |

### Usage Object

```json
{
  "input_tokens": 100,
  "cache_creation_input_tokens": 5000,
  "cache_read_input_tokens": 20000,
  "cache_creation": {
    "ephemeral_5m_input_tokens": 5000,
    "ephemeral_1h_input_tokens": 0
  },
  "output_tokens": 500,
  "service_tier": "standard"
}
```

### Content Block Types

#### Text Block
```json
{
  "type": "text",
  "text": "Response text here"
}
```

#### Thinking Block
```json
{
  "type": "thinking",
  "thinking": "Internal reasoning...",
  "signature": "base64-encoded-signature"
}
```

#### Tool Use Block
```json
{
  "type": "tool_use",
  "id": "toolu_01ABC...",
  "name": "Read",
  "input": {
    "file_path": "/path/to/file"
  }
}
```

#### Tool Result Block
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01ABC...",
  "content": "Tool output text"
}
```

#### Image Block
```json
{
  "type": "image",
  "source": {
    "type": "base64",
    "media_type": "image/png",
    "data": "iVBORw0KGgo..."
  }
}
```

### Tool Result Metadata

Tool result messages may include `toolUseResult`:

```json
{
  "toolUseResult": {
    "mode": "files_with_matches",
    "filenames": ["file1.go", "file2.go"],
    "numFiles": 2
  }
}
```

### File History Snapshot

```json
{
  "type": "file-history-snapshot",
  "messageId": "uuid",
  "snapshot": {
    "messageId": "uuid",
    "trackedFileBackups": {
      "/absolute/path/to/file": "content-hash"
    },
    "timestamp": "2025-12-26T23:15:21.917Z"
  },
  "isSnapshotUpdate": false
}
```

## Special Message Patterns

### Command Messages

User commands appear as:
```json
{
  "message": {
    "role": "user",
    "content": "<command-name>/clear</command-name>\n<command-message>clear</command-message>\n<command-args></command-args>"
  }
}
```

### Local Command Output

```json
{
  "message": {
    "role": "user",
    "content": "<local-command-stdout>output here</local-command-stdout>"
  }
}
```

### Image Metadata

When images are resized:
```json
{
  "message": {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "[Image: original 2124x262, displayed at 2000x247. Multiply coordinates by 1.06 to map to original image.]"
      }
    ]
  },
  "isMeta": true
}
```

## Parsing Tips

1. **Use streaming JSON parser** for large files (can be 100+ MB)
2. **Filter by type** first to reduce processing
3. **Track parentUuid** to reconstruct conversation tree
4. **Sum usage fields** for token totals
5. **Watch for isMeta** to filter system messages
