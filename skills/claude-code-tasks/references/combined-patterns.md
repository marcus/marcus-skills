# Combined Patterns

Examples of combining multiple approaches for sophisticated task orchestration.

## Pattern 1: SDK + Hooks (Quality-Gated Progress)

Monitor tasks via the SDK while hooks enforce quality gates. The SDK gives you real-time visibility; hooks give you deterministic enforcement.

### Setup

`.claude/settings.json`:
```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "command",
          "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/require-tests.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "TodoWrite",
        "hooks": [{
          "type": "command",
          "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/sync-dashboard.sh",
          "async": true
        }]
      }
    ]
  }
}
```

### Orchestration Script

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// The hooks handle enforcement and syncing automatically.
// The SDK script handles monitoring and session management.

let sessionId: string | undefined;

for await (const message of query({
  prompt: "Implement the user registration feature with full test coverage",
  options: {
    maxTurns: 30,
    allowedTools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
    settingSources: ["project"]  // Load project hooks
  }
})) {
  if ("session_id" in message) sessionId = message.session_id;

  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "tool_use" && block.name === "TodoWrite") {
        const todos = block.input.todos;
        const completed = todos.filter(t => t.status === "completed").length;
        console.log(`Progress: ${completed}/${todos.length}`);
      }
    }
  }

  if (message.type === "result" && message.subtype === "success") {
    console.log(`Done. Session: ${sessionId}`);
    console.log(`Cost: $${message.total_cost_usd.toFixed(4)}`);
  }
}
```

## Pattern 2: CLI + Custom MCP (CI Pipeline)

Use `claude -p` in CI with a custom MCP server providing project-specific task tools.

### MCP Server (task-tracker.ts)

```typescript
import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";
import fs from "fs";

const TASK_FILE = process.env.TASK_FILE || "/tmp/ci-tasks.json";

const taskTracker = createSdkMcpServer({
  name: "ci-tasks",
  version: "1.0.0",
  tools: [
    tool("report_ci_status", "Report task completion to CI system",
      {
        task: z.string(),
        status: z.enum(["pass", "fail", "skip"]),
        details: z.string().optional()
      },
      async (args) => {
        const tasks = JSON.parse(fs.readFileSync(TASK_FILE, "utf-8") || "[]");
        tasks.push({ ...args, timestamp: new Date().toISOString() });
        fs.writeFileSync(TASK_FILE, JSON.stringify(tasks, null, 2));
        return { content: [{ type: "text", text: `CI status recorded: ${args.task} = ${args.status}` }] };
      }
    )
  ]
});

export { taskTracker };
```

### CI Script (ci-review.sh)

```bash
#!/bin/bash
set -e

# Run Claude in headless mode, streaming task updates
claude -p "Review this PR for security issues. For each file reviewed, use the report_ci_status tool to log pass/fail." \
  --output-format stream-json \
  --verbose \
  --allowedTools "Read,Grep,Glob,mcp__ci-tasks__report_ci_status" \
  | tee /tmp/claude-output.jsonl \
  | jq -c 'select(.type == "assistant") | .message.content[]? | select(.type == "tool_use" and .name == "TodoWrite") | .input.todos | length' \
  | tail -1

# Check results
FAILURES=$(jq '[.[] | select(.status == "fail")] | length' /tmp/ci-tasks.json)
if [ "$FAILURES" -gt 0 ]; then
  echo "CI: $FAILURES security issues found"
  exit 1
fi
```

## Pattern 3: SDK + MCP + Subagents (Full Orchestration)

The most powerful pattern: custom task tools for external integration, specialized subagents for parallel work, and SDK monitoring for real-time visibility.

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

// Custom MCP server for project management integration
const pmServer = createSdkMcpServer({
  name: "project-mgmt",
  version: "1.0.0",
  tools: [
    tool("create_jira_ticket", "Create a Jira ticket for discovered issues",
      { title: z.string(), priority: z.enum(["P0", "P1", "P2"]), description: z.string() },
      async (args) => {
        // Call Jira API
        return { content: [{ type: "text", text: `JIRA-${Math.random().toString(36).slice(2, 6).toUpperCase()}: ${args.title}` }] };
      }
    ),
    tool("update_dashboard", "Update the team dashboard with current status",
      { metric: z.string(), value: z.number() },
      async (args) => {
        // Call dashboard API
        return { content: [{ type: "text", text: `Dashboard updated: ${args.metric} = ${args.value}` }] };
      }
    )
  ]
});

// Streaming input (required for MCP)
async function* userMessages() {
  yield {
    type: "user" as const,
    message: {
      role: "user" as const,
      content: `
        Perform a comprehensive code review of the payment module:
        1. Use the security-reviewer agent to check for vulnerabilities
        2. Use the test-runner agent to verify test coverage
        3. Create Jira tickets for any issues found
        4. Update the dashboard with the review score
        Track your progress with todos.
      `
    }
  };
}

for await (const message of query({
  prompt: userMessages(),
  options: {
    maxTurns: 50,
    allowedTools: [
      "Read", "Grep", "Glob", "Bash", "Task",
      "mcp__project-mgmt__create_jira_ticket",
      "mcp__project-mgmt__update_dashboard"
    ],
    mcpServers: { "project-mgmt": pmServer },
    agents: {
      "security-reviewer": {
        description: "Security vulnerability scanner",
        prompt: "Check for injection, auth bypass, data exposure, and insecure crypto.",
        tools: ["Read", "Grep", "Glob"],
        model: "opus"
      },
      "test-runner": {
        description: "Test coverage analyzer",
        prompt: "Run tests and analyze coverage. Report uncovered critical paths.",
        tools: ["Bash", "Read", "Grep"],
        model: "sonnet"
      }
    }
  }
})) {
  // Track todos
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "tool_use" && block.name === "TodoWrite") {
        const todos = block.input.todos;
        const done = todos.filter(t => t.status === "completed").length;
        console.log(`[${done}/${todos.length}] ${todos.find(t => t.status === "in_progress")?.activeForm || "idle"}`);
      }
      if (block.type === "tool_use" && block.name === "Task") {
        console.log(`  -> Delegating to ${block.input.subagent_type}: ${block.input.description}`);
      }
    }
  }

  if (message.type === "result" && message.subtype === "success") {
    console.log(`\nReview complete. Cost: $${message.total_cost_usd.toFixed(4)}`);
  }
}
```

## Pattern 4: Hook-Based Todo Sync to External System

Use an async PostToolUse hook to push every todo update to an external system (Slack, database, dashboard) without blocking Claude.

`.claude/hooks/sync-todos.py`:
```python
#!/usr/bin/env python3
import json, sys, os, urllib.request

data = json.load(sys.stdin)
todos = data.get("tool_input", {}).get("todos", [])

webhook_url = os.environ.get("TODO_WEBHOOK_URL")
if not webhook_url:
    sys.exit(0)

payload = json.dumps({
    "session_id": data.get("session_id"),
    "todos": todos,
    "stats": {
        "total": len(todos),
        "completed": sum(1 for t in todos if t["status"] == "completed"),
        "in_progress": sum(1 for t in todos if t["status"] == "in_progress"),
    }
}).encode()

req = urllib.request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"})
urllib.request.urlopen(req, timeout=5)
```

`.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "TodoWrite",
        "hooks": [{
          "type": "command",
          "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/sync-todos.py",
          "async": true,
          "timeout": 10
        }]
      }
    ]
  }
}
```
