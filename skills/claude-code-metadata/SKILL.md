---
name: claude-code-metadata
description: Comprehensive guide to Claude Code's local data storage, session formats, token tracking, and metadata structures. Use when building dashboards, analytics tools, migration scripts, or any application that needs to read Claude Code's local data. Covers JSONL session format, stats-cache.json structure, settings hierarchy, file history, and all ~/.claude directory contents.
---

# Claude Code Metadata & Data Formats

Complete technical reference for Claude Code's local data storage architecture. All data is stored locally in `~/.claude/`.

## Directory Structure Overview

```
~/.claude/
├── CLAUDE.md                    # User memory file (personal instructions)
├── settings.json                # User settings (global)
├── settings.json.backup         # Backup of settings
├── stats-cache.json             # Token usage statistics cache
├── history.jsonl                # Session index/metadata
│
├── projects/                    # Session transcripts by project path
│   └── -Users-name-project/     # Path encoded as directory name
│       ├── session-uuid.jsonl   # Main session files
│       └── agent-xyz.jsonl      # Agent/subagent sessions
│
├── session-env/                 # Session environment snapshots
│   └── session-uuid/            # Per-session env directory
│
├── todos/                       # Todo lists per session/agent
│   └── session-uuid-agent-uuid.json
│
├── plans/                       # Plan mode files (markdown)
│   └── adjective-verb-noun.md   # Random generated names
│
├── debug/                       # Debug logs per session
│   └── session-uuid.txt
│   └── latest                   # Symlink to most recent
│
├── file-history/                # File backup history
│   └── session-uuid/
│       └── content-hash@v1      # Versioned file backups
│
├── shell-snapshots/             # Shell state snapshots
│   └── snapshot-zsh-timestamp-random.sh
│
├── skills/                      # User skills (symlinks or dirs)
│   └── skill-name/
│       ├── SKILL.md
│       └── references/
│
├── agents/                      # Custom agent definitions
│   └── agent-name.md
│
├── plugins/                     # Plugin system
│   ├── config.json
│   ├── installed_plugins.json
│   ├── known_marketplaces.json
│   ├── cache/                   # Downloaded plugin cache
│   ├── marketplaces/            # Marketplace repos
│   └── repos/
│
├── config/                      # Additional config
│   └── notification_states.json
│
├── statsig/                     # Feature flags (Statsig)
│   ├── statsig.cached.evaluations.*
│   ├── statsig.failed_logs.*
│   ├── statsig.last_modified_time.*
│   ├── statsig.session_id.*
│   └── statsig.stable_id.*
│
├── chrome/                      # Chrome extension support
│   └── chrome-native-host
│
├── ide/                         # IDE integration (empty by default)
│
└── telemetry/                   # Telemetry data (empty by default)
```

## Session JSONL Format

Sessions are stored as JSON Lines files. Each line is a complete JSON object representing a message or event.

### Message Types

| type | Description |
|------|-------------|
| `user` | User messages |
| `assistant` | Claude responses |
| `summary` | Context summaries |
| `file-history-snapshot` | File backup checkpoints |

### User Message Schema

```json
{
  "parentUuid": "previous-message-uuid",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/working/directory",
  "sessionId": "session-uuid",
  "version": "2.0.76",
  "gitBranch": "main",
  "type": "user",
  "message": {
    "role": "user",
    "content": "message text or array of content blocks"
  },
  "isMeta": false,
  "uuid": "unique-message-id",
  "timestamp": "2025-12-26T23:15:21.914Z"
}
```

### Assistant Message Schema

```json
{
  "parentUuid": "user-message-uuid",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/working/directory",
  "sessionId": "session-uuid",
  "version": "2.0.76",
  "gitBranch": "main",
  "slug": "adjective-verb-noun",
  "message": {
    "model": "claude-opus-4-5-20251101",
    "id": "msg_01XYZ...",
    "type": "message",
    "role": "assistant",
    "content": [
      {
        "type": "thinking",
        "thinking": "internal reasoning...",
        "signature": "base64-signature..."
      },
      {
        "type": "text",
        "text": "response text"
      },
      {
        "type": "tool_use",
        "id": "toolu_01ABC...",
        "name": "ToolName",
        "input": { "param": "value" }
      }
    ],
    "stop_reason": "end_turn",
    "stop_sequence": null,
    "usage": {
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
  },
  "requestId": "req_01XYZ...",
  "type": "assistant",
  "uuid": "message-uuid",
  "timestamp": "2025-12-26T23:16:04.923Z"
}
```

### Tool Result Message Schema

```json
{
  "parentUuid": "tool-use-message-uuid",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/working/directory",
  "sessionId": "session-uuid",
  "version": "2.0.76",
  "gitBranch": "main",
  "slug": "adjective-verb-noun",
  "type": "user",
  "message": {
    "role": "user",
    "content": [
      {
        "tool_use_id": "toolu_01ABC...",
        "type": "tool_result",
        "content": "tool output text"
      }
    ]
  },
  "uuid": "result-uuid",
  "timestamp": "2025-12-26T23:16:05.510Z",
  "toolUseResult": {
    "mode": "files_with_matches",
    "filenames": ["file1.go", "file2.go"],
    "numFiles": 2
  }
}
```

### File History Snapshot Schema

```json
{
  "type": "file-history-snapshot",
  "messageId": "associated-message-uuid",
  "snapshot": {
    "messageId": "associated-message-uuid",
    "trackedFileBackups": {
      "/path/to/file": "content-hash"
    },
    "timestamp": "2025-12-26T23:15:21.917Z"
  },
  "isSnapshotUpdate": false
}
```

### Content Types in Messages

Messages can have `content` as:
- **String**: Plain text content
- **Array**: Multiple content blocks

Content block types:
- `text`: Plain text `{ "type": "text", "text": "..." }`
- `image`: Base64 image `{ "type": "image", "source": { "type": "base64", "media_type": "image/png", "data": "..." } }`
- `thinking`: Model reasoning `{ "type": "thinking", "thinking": "...", "signature": "..." }`
- `tool_use`: Tool invocation `{ "type": "tool_use", "id": "...", "name": "...", "input": {...} }`
- `tool_result`: Tool output `{ "type": "tool_result", "tool_use_id": "...", "content": "..." }`

## Stats Cache Format (stats-cache.json)

Aggregated usage statistics cached locally.

```json
{
  "version": 1,
  "lastComputedDate": "2025-12-25",
  "totalSessions": 766,
  "totalMessages": 58731,
  "firstSessionDate": "2025-11-12T06:27:12.809Z",

  "dailyActivity": [
    {
      "date": "2025-12-24",
      "messageCount": 4800,
      "sessionCount": 16,
      "toolCallCount": 1464
    }
  ],

  "dailyModelTokens": [
    {
      "date": "2025-12-24",
      "tokensByModel": {
        "claude-opus-4-5-20251101": 33212,
        "claude-sonnet-4-5-20250929": 103056,
        "claude-haiku-4-5-20251001": 272249
      }
    }
  ],

  "modelUsage": {
    "claude-opus-4-5-20251101": {
      "inputTokens": 1640347,
      "outputTokens": 2475769,
      "cacheReadInputTokens": 1242320484,
      "cacheCreationInputTokens": 66151371,
      "webSearchRequests": 0,
      "costUSD": 0,
      "contextWindow": 0
    }
  },

  "hourCounts": {
    "9": 58,
    "10": 43,
    "17": 59,
    "18": 94
  },

  "longestSession": {
    "sessionId": "uuid",
    "duration": 96242264,
    "messageCount": 4,
    "timestamp": "2025-11-17T02:12:38.105Z"
  }
}
```

## Settings Format (settings.json)

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "opus",
  "alwaysThinkingEnabled": true,

  "hooks": {
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'hook output'"
          }
        ]
      }
    ],
    "SessionStart": []
  },

  "statusLine": {
    "type": "command",
    "command": "shell command for status line"
  },

  "enabledPlugins": {
    "plugin-name@marketplace": true
  },

  "feedbackSurveyState": {
    "lastShownTime": 1754025174206
  }
}
```

### Hook Event Types

- `SessionStart`: When a new session begins
- `PreCompact`: Before context compaction
- `SubagentStart`: When a subagent is spawned

## History Index (history.jsonl)

Each line contains session metadata:

```json
{
  "display": "user message preview",
  "pastedContents": {},
  "timestamp": 1766792756159,
  "project": "/Users/name/code/project",
  "sessionId": "session-uuid"
}
```

## Todo Format (todos/*.json)

```json
[
  {
    "content": "Task description",
    "status": "in_progress",
    "activeForm": "Working on task"
  }
]
```

Status values: `pending`, `in_progress`, `completed`

## Installed Plugins Format

```json
{
  "version": 2,
  "plugins": {
    "plugin-name@marketplace-name": [
      {
        "scope": "user",
        "installPath": "/path/to/plugin",
        "version": "1.0.0",
        "installedAt": "2025-12-04T02:42:33.270Z",
        "lastUpdated": "2025-12-04T02:42:33.270Z",
        "gitCommitSha": "abc123...",
        "isLocal": true
      }
    ]
  }
}
```

## Agent Definition Format

Markdown file with YAML frontmatter:

```markdown
---
name: agent-name
description: When to use this agent
model: sonnet
color: green
---

Agent system prompt instructions here...
```

## Memory File Hierarchy

Priority order (highest to lowest):

| Priority | Location | Scope |
|----------|----------|-------|
| 1 | `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | Enterprise |
| 2 | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Project (team) |
| 3 | `./.claude/rules/*.md` | Project rules |
| 4 | `~/.claude/CLAUDE.md` | User (all projects) |
| 4b | `./CLAUDE.local.md` | Project local |

### Import Syntax

```markdown
See @README for project overview.
@docs/instructions.md
@~/.claude/custom-rules.md
```

## File History Backup Format

Files in `file-history/session-uuid/`:
- Filename: `content-hash@vN` (e.g., `89a91e02ba2f0439@v1`)
- Content: Raw file contents at that version

## Debug Log Format

Plain text with timestamps:

```
2025-11-25T19:05:43.547Z [DEBUG] Message here...
```

## Shell Snapshot Format

Shell script capturing environment:

```bash
# Snapshot file
# Unset all aliases to avoid conflicts with functions
unalias -a 2>/dev/null || true
# Functions
function_name () { ... }
# Environment variables
export VAR=value
```

## Notification States (config/notification_states.json)

```json
{
  "switch_to_custom": {
    "triggered": false,
    "timestamp": null
  },
  "exceed_max_limit": {
    "triggered": true,
    "timestamp": "2025-09-27T19:00:38.269745"
  },
  "tokens_will_run_out": {
    "triggered": false,
    "timestamp": null
  },
  "cost_will_exceed": {
    "triggered": true,
    "timestamp": "2025-09-27T16:56:18.406988"
  }
}
```

## Statsig Feature Flags

Files in `statsig/`:
- `statsig.cached.evaluations.*`: Feature flag cache
- `statsig.failed_logs.*`: Failed telemetry
- `statsig.stable_id.*`: User identifier
- `statsig.session_id.*`: Session identifier

## Project Path Encoding

Project paths become directory names by replacing `/` with `-`:
- `/Users/name/code/project` -> `-Users-name-code-project`

## Token Usage Calculation

From assistant messages, extract:
- `usage.input_tokens`: Direct input tokens
- `usage.cache_creation_input_tokens`: New cache entries
- `usage.cache_read_input_tokens`: Cache hits
- `usage.output_tokens`: Response tokens

Cache efficiency = `cache_read_input_tokens / (cache_read_input_tokens + input_tokens)`

## Session Retention

Default: 30 days. Configure with `cleanupPeriodDays` setting.

## Key UUIDs

All UUIDs follow RFC 4122 format:
- Session IDs: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Message UUIDs: Same format, linked via `parentUuid`
- Request IDs: `req_` prefix
- Tool IDs: `toolu_` prefix
- Message IDs: `msg_` prefix

## Model Identifiers

Common model IDs:
- `claude-opus-4-5-20251101`
- `claude-sonnet-4-5-20250929`
- `claude-haiku-4-5-20251001`

## Cost Calculation Reference

Per-million tokens (approximate):
- Haiku: $0.25 input / $1.25 output
- Sonnet: $3.00 input / $15.00 output
- Opus: $5.00 input / $25.00 output
- Cache read: 90% discount
- Batch: 50% discount

## Useful Queries

### Count total tokens per session
Parse JSONL, sum `usage.input_tokens + usage.output_tokens` for `type: assistant`.

### Find all sessions for a project
List files in `projects/-path-to-project/`.

### Get session timeline
Sort messages by `timestamp` field.

### Reconstruct conversation tree
Follow `parentUuid` chains to build message tree.

## Third-Party Tools

- **ccusage**: CLI for analyzing usage from JSONL files
- **Claude Code Usage Monitor**: Real-time terminal dashboard
- **LiteLLM**: Proxy for tracking enterprise usage

## References

- [Claude Code Docs - Memory](https://code.claude.com/docs/en/memory)
- [Claude Code Docs - Costs](https://code.claude.com/docs/en/costs)
- [Usage and Cost API](https://platform.claude.com/docs/en/build-with-claude/usage-cost-api)
