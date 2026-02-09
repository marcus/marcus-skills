---
name: claude-code-tasks
description: |
  Guide for programmatically interacting with Claude Code's task/todo system from external code. Use this skill whenever the user wants to: monitor or track Claude Code tasks from scripts, build automations that react to todo updates, create hooks that enforce task completion criteria, build custom task management MCP tools, use the Agent SDK to watch or control task progress, stream task updates via the CLI, integrate Claude Code's task system with external services, or orchestrate work across subagents. Also trigger when users mention "TodoWrite", "TaskCompleted", "Agent SDK tasks", "programmatic tasks", "task hooks", or "claude code automation" — even if they don't explicitly say "skill".
---

# Programmatic Task Management for Claude Code

Five verified approaches for interacting with Claude Code's task/todo system from code. Each suits different use cases — from lightweight shell scripts to full orchestration systems.

## Quick Reference: Which Approach to Use

| Goal | Approach | Language |
|------|----------|----------|
| Watch task progress in real time | Agent SDK message stream | Python / TypeScript |
| React to task changes with side effects | Hooks (PostToolUse on TodoWrite) | Shell / Python |
| Block task completion until criteria met | Hooks (TaskCompleted) | Shell / Python / LLM |
| Add custom task-like tools Claude can call | Custom MCP tools | Python / TypeScript |
| Parse task updates from CLI output | Headless CLI streaming | Any (parses NDJSON) |
| Delegate work to specialized sub-agents | Subagents via Agent SDK | Python / TypeScript |

## Approach 1: Agent SDK Message Stream

The most direct way to monitor tasks programmatically. The `query()` function returns an async generator. Every `TodoWrite` call appears as a `tool_use` block in the stream.

**Install:**
```bash
npm install @anthropic-ai/claude-agent-sdk   # TypeScript
pip install claude-agent-sdk                  # Python
```

### TodoWrite Schema

```typescript
// Input: complete replacement of the todo list each time
interface TodoWriteInput {
  todos: Array<{
    content: string;                              // Imperative form: "Fix the bug"
    status: 'pending' | 'in_progress' | 'completed';
    activeForm: string;                           // Present participle: "Fixing the bug"
  }>;
}

// Output: confirmation with stats
interface TodoWriteOutput {
  message: string;
  stats: { total: number; pending: number; in_progress: number; completed: number };
}
```

Only one todo should be `in_progress` at any time. The list is replaced wholesale on each call (not diffed).

### TypeScript: Monitor Todos

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Refactor the auth module and track your progress",
  options: { maxTurns: 15 }
})) {
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "tool_use" && block.name === "TodoWrite") {
        const todos = block.input.todos;
        console.log("--- Todo Update ---");
        todos.forEach((todo, i) => {
          const icon = { completed: "done", in_progress: ">>", pending: "  " }[todo.status];
          console.log(`  [${icon}] ${todo.content}`);
        });
      }
    }
  }
}
```

### Python: Monitor Todos

```python
from claude_agent_sdk import query, AssistantMessage, ToolUseBlock

async for message in query(
    prompt="Refactor the auth module and track your progress",
    options={"max_turns": 15}
):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolUseBlock) and block.name == "TodoWrite":
                todos = block.input["todos"]
                for todo in todos:
                    status_icon = {"completed": "done", "in_progress": ">>", "pending": "  "}
                    print(f"  [{status_icon[todo['status']]}] {todo['content']}")
```

For a full real-time progress tracker class with change detection, see `references/progress-tracker.md`.

## Approach 2: Hooks

Hooks fire at lifecycle points and are configured in `.claude/settings.json` (project-scoped) or `~/.claude/settings.json` (global). Three hook handler types exist: `command` (shell script), `prompt` (single LLM call), and `agent` (multi-turn subagent with tool access).

### Intercept TodoWrite Updates

Use `PostToolUse` with matcher `"TodoWrite"` to react after a todo update, or `PreToolUse` to validate/block before it happens.

**Log every todo update** (`.claude/settings.json`):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "TodoWrite",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/log-todos.sh"
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/log-todos.sh`:
```bash
#!/bin/bash
INPUT=$(cat)
TODOS=$(echo "$INPUT" | jq '.tool_input.todos')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "{\"timestamp\": \"$TIMESTAMP\", \"todos\": $TODOS}" >> "$CLAUDE_PROJECT_DIR/.claude/todo-log.jsonl"
exit 0
```

**Block certain todos via PreToolUse:**
```bash
#!/bin/bash
INPUT=$(cat)
FORBIDDEN=$(echo "$INPUT" | jq -r '.tool_input.todos[].content' | grep -i "deploy to production")
if [ -n "$FORBIDDEN" ]; then
  jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:"Production deploys require manual approval"}}'
else
  exit 0
fi
```

### TaskCompleted Hook

Fires when any task is being marked as completed. Exit code 2 blocks completion and feeds stderr back to the agent as corrective feedback. No matcher support — fires on every completion.

**Input fields:** `task_id`, `task_subject`, `task_description` (optional), `teammate_name` (optional), `team_name` (optional).

**Require tests to pass:**
```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [{ "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/require-tests.sh" }]
      }
    ]
  }
}
```

```bash
#!/bin/bash
INPUT=$(cat)
TASK=$(echo "$INPUT" | jq -r '.task_subject')
if ! npm test 2>&1; then
  echo "Tests failing. Fix before completing: $TASK" >&2
  exit 2
fi
exit 0
```

**LLM-based completion gate:**
```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "prompt",
          "prompt": "Evaluate whether this task is truly complete: $ARGUMENTS. Check all subtasks are done and no errors remain.",
          "timeout": 30
        }]
      }
    ]
  }
}
```

The LLM responds with `{"ok": true}` or `{"ok": false, "reason": "..."}`.

**Agent-based deep verification:**
```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "agent",
          "prompt": "Verify task completion: check tests pass, no TODO comments in changed files, docs updated. Context: $ARGUMENTS",
          "timeout": 120
        }]
      }
    ]
  }
}
```

Agent hooks spawn a subagent with access to Read, Grep, and Glob tools for multi-turn investigation.

### Other Useful Hook Events

| Event | Matcher | Use Case |
|-------|---------|----------|
| `Stop` | none | Prevent Claude from stopping if tasks remain incomplete |
| `SubagentStart` | agent type | React when a subagent spawns |
| `SubagentStop` | agent type | Block subagent from finishing; can force more work |
| `SessionStart` | startup/resume | Inject task context at session start |

For the complete hook reference (all events, inputs, outputs, exit codes), see `references/hooks-reference.md`.

## Approach 3: Custom MCP Tools

Build your own task management tools as an in-process MCP server. Claude can call these alongside its built-in TodoWrite.

**Important:** Custom MCP tools require streaming input mode (async generator for the `prompt` parameter, not a plain string).

### TypeScript: Custom Task Board

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const taskBoard = createSdkMcpServer({
  name: "task-board",
  version: "1.0.0",
  tools: [
    tool("create_task", "Create a task on the external board",
      { title: z.string(), priority: z.enum(["low", "medium", "high"]) },
      async (args) => {
        // Insert into DB, call API, etc.
        return { content: [{ type: "text", text: `Created: ${args.title} [${args.priority}]` }] };
      }
    ),
    tool("complete_task", "Mark a task as done",
      { task_id: z.string() },
      async (args) => {
        return { content: [{ type: "text", text: `Completed: ${args.task_id}` }] };
      }
    )
  ]
});

// Streaming input is required for MCP servers
async function* messages() {
  yield { type: "user" as const, message: { role: "user" as const, content: "Create a task to fix the login bug" } };
}

for await (const msg of query({
  prompt: messages(),
  options: {
    mcpServers: { "task-board": taskBoard },
    allowedTools: ["mcp__task-board__create_task", "mcp__task-board__complete_task"]
  }
})) {
  if ("result" in msg) console.log(msg.result);
}
```

### Python: Custom Task Board

```python
from claude_agent_sdk import tool, create_sdk_mcp_server
from typing import Any

@tool("create_task", "Create a task on the external board", {"title": str, "priority": str})
async def create_task(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Created: {args['title']} [{args['priority']}]"}]}

@tool("complete_task", "Mark a task as done", {"task_id": str})
async def complete_task(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Completed: {args['task_id']}"}]}

task_server = create_sdk_mcp_server(name="task-board", version="1.0.0", tools=[create_task, complete_task])
```

Tool names follow the pattern `mcp__{server_name}__{tool_name}` (e.g., `mcp__task-board__create_task`).

## Approach 4: CLI Headless Streaming

Parse task updates from `claude -p` output without any SDK code. Ideal for shell scripts, CI/CD, and language-agnostic integrations.

### Stream and Filter TodoWrite Events

```bash
claude -p "Refactor this module and track progress" \
  --output-format stream-json \
  --verbose \
  --include-partial-messages | \
  jq -c 'select(.type == "assistant") |
    .message.content[]? |
    select(.type == "tool_use" and .name == "TodoWrite") |
    .input.todos'
```

### Session Management

```bash
# Capture session ID
SESSION=$(claude -p "Start analysis" --output-format json | jq -r '.session_id')

# Resume later
claude -p "Continue the analysis" --resume "$SESSION"

# Or just continue most recent
claude -p "What's left to do?" --continue
```

### Key CLI Flags

| Flag | Purpose |
|------|---------|
| `-p` | Non-interactive (headless) mode |
| `--output-format stream-json` | NDJSON streaming for real-time parsing |
| `--output-format json` | Structured JSON with session_id and metadata |
| `--verbose` | Full turn-by-turn output |
| `--include-partial-messages` | Token-level streaming |
| `--continue` / `--resume <id>` | Session continuity |
| `--allowedTools "Bash,Read,Edit"` | Auto-approve specific tools |
| `--append-system-prompt "..."` | Add instructions while keeping defaults |

## Approach 5: Subagents

Define specialized agents that handle focused subtasks. The main agent delegates via the `Task` tool.

```typescript
for await (const message of query({
  prompt: "Review auth security, then run tests",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Bash", "Task"],
    agents: {
      "security-reviewer": {
        description: "Security code review specialist.",
        prompt: "Identify vulnerabilities, injection risks, and auth flaws.",
        tools: ["Read", "Grep", "Glob"],   // read-only
        model: "sonnet"
      },
      "test-runner": {
        description: "Test execution and analysis specialist.",
        prompt: "Run test suites and analyze failures.",
        tools: ["Bash", "Read", "Grep"]
      }
    }
  }
})) {
  // Detect delegation
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "tool_use" && block.name === "Task") {
        console.log(`Delegated to: ${block.input.subagent_type}`);
      }
    }
  }
}
```

Key rules: subagents cannot spawn their own subagents; include `Task` in `allowedTools` to enable delegation; omit `tools` to inherit all parent tools.

For resuming subagents and advanced patterns, see `references/subagent-patterns.md`.

## Combining Approaches

These compose naturally. Common combinations:

- **SDK + Hooks:** Monitor via message stream while hooks enforce quality gates.
- **CLI + Custom MCP:** Use `claude -p` in CI with project-specific task tools.
- **SDK + MCP + Subagents:** Full orchestration — custom task tools, specialized agents, real-time monitoring.

For detailed combined examples, see `references/combined-patterns.md`.

## Official Documentation

- [Todo Tracking (Agent SDK)](https://platform.claude.com/docs/en/agent-sdk/todo-tracking)
- [Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Custom Tools](https://platform.claude.com/docs/en/agent-sdk/custom-tools)
- [Headless / Programmatic CLI](https://code.claude.com/docs/en/headless)
- [Subagents](https://platform.claude.com/docs/en/agent-sdk/subagents)
- [TypeScript SDK Reference](https://platform.claude.com/docs/en/agent-sdk/typescript)
- [Python SDK Reference](https://platform.claude.com/docs/en/agent-sdk/python)
