# Hooks Reference for Task Management

Condensed reference for hooks most relevant to task/todo management. For the complete hooks reference covering all events, see [code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks).

## Configuration

Hooks are defined in JSON settings files at three levels:

| Location | Scope |
|----------|-------|
| `~/.claude/settings.json` | All projects (user-global) |
| `.claude/settings.json` | Single project (committable) |
| `.claude/settings.local.json` | Single project (gitignored) |

## Handler Types

| Type | Description | Default Timeout |
|------|-------------|-----------------|
| `command` | Shell script, receives JSON on stdin | 600s |
| `prompt` | Single LLM call, returns `{ok, reason}` | 30s |
| `agent` | Multi-turn subagent with Read/Grep/Glob | 60s |

## Common Input Fields (All Events)

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse"
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success. Parse stdout for JSON output. |
| 2 | Blocking error. Stderr is fed back to agent (for blockable events). |
| Other | Non-blocking error. Stderr shown in verbose mode. |

## Task-Relevant Events

### PreToolUse (matcher: tool name)

Fires before a tool call executes. Can block it.

**Matcher for todos:** `"TodoWrite"`

**Additional input fields:** `tool_name`, `tool_input`, `tool_use_id`

**Decision control via JSON stdout:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Reason shown to user (allow/ask) or Claude (deny)",
    "updatedInput": { "field": "modified value" },
    "additionalContext": "Extra context for Claude"
  }
}
```

### PostToolUse (matcher: tool name)

Fires after a tool call succeeds. Cannot block (already happened).

**Matcher for todos:** `"TodoWrite"`

**Additional input fields:** `tool_name`, `tool_input`, `tool_response`, `tool_use_id`

**Decision control:**
```json
{
  "decision": "block",
  "reason": "Explanation shown to Claude",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Extra info for Claude"
  }
}
```

### TaskCompleted (no matcher)

Fires when any task is marked as completed. Always fires on every completion.

**Additional input fields:**
```json
{
  "task_id": "task-001",
  "task_subject": "Implement login endpoint",
  "task_description": "Add POST /api/login with JWT",
  "teammate_name": "implementer",
  "team_name": "my-project"
}
```

`task_description`, `teammate_name`, and `team_name` may be absent.

**Decision control:** Exit code 2 only. Stderr is fed back as feedback.

### Stop (no matcher)

Fires when Claude finishes responding. Can prevent stopping.

**Additional input:** `stop_hook_active` (boolean — true if already continuing from a previous Stop hook).

**Decision control:**
```json
{
  "decision": "block",
  "reason": "Tasks remain incomplete. Continue working on..."
}
```

Check `stop_hook_active` to prevent infinite loops.

### SubagentStart (matcher: agent type)

Fires when a subagent spawns. Cannot block, but can inject context.

**Input:** `agent_id`, `agent_type`

**Output:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SubagentStart",
    "additionalContext": "Follow security guidelines for this task"
  }
}
```

### SubagentStop (matcher: agent type)

Fires when a subagent finishes. Can prevent stopping (same pattern as Stop).

**Input:** `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`

### SessionStart (matcher: startup|resume|clear|compact)

Fires on session start. Good for injecting task context.

**Input:** `source`, `model`, optional `agent_type`

**Output:** `additionalContext` string added to Claude's context. Can also write env vars to `$CLAUDE_ENV_FILE`.

### SessionEnd (matcher: exit reason)

Fires on session end. Cannot block. Good for cleanup/logging.

**Input:** `reason` (clear, logout, prompt_input_exit, etc.)

## Async Hooks

Add `"async": true` to run hooks in the background without blocking Claude. Only for `command` type. Async hooks cannot block or control behavior — they fire-and-forget. Output is delivered on the next conversation turn.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "TodoWrite",
        "hooks": [{
          "type": "command",
          "command": "/path/to/sync-to-dashboard.sh",
          "async": true,
          "timeout": 30
        }]
      }
    ]
  }
}
```

## Debugging

Run `claude --debug` to see hook execution details. Toggle verbose mode with Ctrl+O in interactive mode.
