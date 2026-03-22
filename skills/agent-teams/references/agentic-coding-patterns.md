# Agentic Coding Patterns: Codex App-Server & Claude Agent SDK

*Reference for agent-teams skill — full agentic coding with streaming output*

This document covers the two production-grade patterns for programmatic agentic coding with streaming output: the **Codex App-Server Protocol** (OpenAI) and the **Claude Agent SDK** (Anthropic). Both support full agentic capability including subagent spawning.

---

## 1. Codex App-Server Protocol

### Overview

The Codex app-server is a JSON-RPC 2.0 server that runs as a subprocess, communicating over stdio (JSONL) or WebSocket. It's the same interface that powers the Codex VS Code extension and is the protocol OpenAI's Symphony spec uses for agent orchestration.

**Source:** [openai/codex/codex-rs/app-server](https://github.com/openai/codex/tree/main/codex-rs/app-server)
**Docs:** [developers.openai.com/codex/app-server](https://developers.openai.com/codex/app-server/)

### Transport

- **stdio** (default): `codex app-server` — newline-delimited JSON on stdout, commands on stdin
- **WebSocket** (experimental): `codex app-server --listen ws://127.0.0.1:4500`

### Session Lifecycle

```
Client                          App-Server
  |                                 |
  |── initialize ──────────────────>|  (clientInfo, capabilities)
  |<────────── result ──────────────|  (serverInfo)
  |── initialized ─────────────────>|  (notification, no id)
  |                                 |
  |── thread/start ────────────────>|  (model, approvalPolicy, sandbox, cwd)
  |<────────── result ──────────────|  (thread.id)
  |<── thread/started ──────────────|  (notification)
  |                                 |
  |── turn/start ──────────────────>|  (threadId, input, cwd, title)
  |<── turn/started ────────────────|
  |<── item/started ────────────────|  (repeated — tool calls, messages)
  |<── item/agentMessage/delta ─────|  (streaming text chunks)
  |<── item/completed ──────────────|
  |<── turn/completed ──────────────|  (final status + usage)
  |                                 |
  |── turn/start ──────────────────>|  (continuation on same threadId)
  |   ...                           |
```

### Key Concepts

**Thread:** A conversation between user and agent. Contains turns.
**Turn:** A single user request + all agent work that follows. Contains items.
**Item:** A unit of I/O — user message, agent message, command run, file change, tool call.

### Initialization

```json
{"method": "initialize", "id": 0, "params": {
  "clientInfo": {"name": "perch", "title": "Perch Dispatch", "version": "1.0.0"},
  "capabilities": {"experimentalApi": true}
}}
{"method": "initialized", "params": {}}
```

### Starting a Thread + Turn

```json
{"method": "thread/start", "id": 1, "params": {
  "model": "gpt-5.4",
  "approvalPolicy": "auto-edit",
  "sandbox": "on",
  "cwd": "/workspaces/PROJECT-123"
}}

{"method": "turn/start", "id": 2, "params": {
  "threadId": "thr_abc123",
  "input": [{"type": "text", "text": "Implement the user authentication module based on..."}],
  "cwd": "/workspaces/PROJECT-123",
  "title": "PROJECT-123: Auth module"
}}
```

### Streaming Events

After `turn/start`, read JSONL from stdout:

| Notification | Purpose |
|-------------|---------|
| `turn/started` | Turn began |
| `item/started` | New item (tool call, message, etc.) |
| `item/agentMessage/delta` | Streaming text chunk from agent |
| `item/completed` | Item finished |
| `turn/completed` | Turn done — includes final status and token usage |
| `thread/status/changed` | Thread runtime status changed |

### Multi-Turn Continuation

Reuse the same `threadId` for follow-up turns. First turn gets the full prompt; continuation turns send lighter guidance:

```json
{"method": "turn/start", "id": 3, "params": {
  "threadId": "thr_abc123",
  "input": [{"type": "text", "text": "The review found issues with input validation. Please fix the sanitization in auth_handler.go."}],
  "cwd": "/workspaces/PROJECT-123"
}}
```

### Steering an Active Turn

Append input to an in-flight turn without starting a new one:

```json
{"method": "turn/steer", "id": 4, "params": {
  "threadId": "thr_abc123",
  "input": [{"type": "text", "text": "Also check the session token expiry logic."}]
}}
```

### Additional Capabilities

- `turn/interrupt` — cancel an in-flight turn
- `review/start` — kick off the built-in code reviewer
- `thread/resume` — reopen an existing thread
- `thread/fork` — branch history into a new thread
- `thread/compact/start` — trigger context compaction
- `thread/rollback` — drop last N turns
- `model/list` — discover available models
- `command/exec` — run a command under the sandbox without a thread

### Schema Generation

Generate TypeScript types or JSON Schema for the exact version you're running:

```bash
codex app-server generate-ts --out ./schemas
codex app-server generate-json-schema --out ./schemas
```

### Subagent Capability

Codex has **full sub-agent support** enabled by default. Key details:

**Spawning:** Codex spawns sub-agents when explicitly asked in the prompt. Sub-agents run in parallel; Codex handles orchestration (spawning, routing, waiting, closing threads).

**Built-in agents:** `default` (general), `worker` (execution), `explorer` (read-heavy exploration).

**Custom agents:** Defined as TOML files in `.codex/agents/` (project) or `~/.codex/agents/` (global):

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
model_reasoning_effort = "high"
sandbox_mode = "read-only"
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
"""
nickname_candidates = ["Atlas", "Delta", "Echo"]
```

Required fields: `name`, `description`, `developer_instructions`. Optional: `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`, `nickname_candidates`.

**Global settings** (in `config.toml` under `[agents]`):
- `agents.max_threads` — concurrent thread cap (default: 6)
- `agents.max_depth` — nesting depth (default: 1, direct children only)
- `agents.job_max_runtime_seconds` — timeout per worker

**CSV fan-out:** `spawn_agents_on_csv` tool reads a CSV, spawns one worker per row, exports combined results. Each worker calls `report_agent_job_result`. Good for batch audits, migrations, bulk reviews.

**Interactive features:** `/agent` CLI command to switch threads, steer running sub-agents, stop them. Approval requests surface from inactive threads with source labels.

**Sandbox:** Sub-agents inherit parent's sandbox policy. Can override per custom agent (e.g., `sandbox_mode = "read-only"` for reviewers).

### Go Integration Pattern

Launch as subprocess, parse JSONL from stdout:

```go
cmd := exec.CommandContext(ctx, "bash", "-lc", "codex app-server")
cmd.Dir = workspacePath
cmd.Stdin = stdinPipe
cmd.Stdout = stdoutPipe
cmd.Stderr = os.Stderr  // diagnostics only, not protocol

scanner := bufio.NewScanner(stdoutPipe)
scanner.Buffer(make([]byte, 10*1024*1024), 10*1024*1024) // 10MB max line

for scanner.Scan() {
    var msg map[string]any
    json.Unmarshal(scanner.Bytes(), &msg)
    // Route based on msg["method"] or msg["id"]
}
```

---

## 2. Claude Agent SDK

### Overview

The Claude Agent SDK is the infrastructure behind Claude Code, exposed as a library. Renamed from "Claude Code SDK" in 2025. Available in both **Python** (`claude-agent-sdk` on PyPI, v0.1.48+) and **TypeScript** (`@anthropic-ai/claude-agent-sdk` on npm, v0.2.71+).

The core is a `query()` function that returns an async generator of typed messages as the agent works.

### Installation

```bash
# Python
pip install claude-agent-sdk

# TypeScript
npm install @anthropic-ai/claude-agent-sdk
```

### Basic Usage (TypeScript)

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Implement the authentication module with bcrypt password hashing",
  options: {
    model: "sonnet",
    allowedTools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
    permissionMode: "acceptEdits",
    maxTurns: 50,
    cwd: "/workspaces/PROJECT-123",
  }
})) {
  switch (message.type) {
    case "system":
      if (message.subtype === "init") sessionId = message.session_id;
      break;
    case "assistant":
      process.stdout.write(message.content);  // streaming text
      break;
    case "tool":
      console.log(`Tool: ${message.tool_name}`, message.content);
      break;
    case "result":
      if (message.subtype === "success") {
        console.log("Done:", message.result);
        console.log(`Cost: $${message.total_cost_usd}`);
      }
      break;
  }
}
```

### Built-in Tools

The SDK includes 14+ built-in tools referenced by string name (no JSON schema required):

| Tool | Purpose |
|------|---------|
| `Read` | Read file contents |
| `Write` | Write/create files |
| `Edit` | Surgical file edits |
| `Bash` | Execute shell commands |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `WebSearch` | Search the web |
| `WebFetch` | Fetch URL content |
| `Task` | Spawn a subagent (required for subagent orchestration) |

### Subagent Orchestration

Define agent types in the `agents` parameter. Include `Task` in the parent's `allowedTools`. Claude decides when to spawn subagents and whether to parallelize.

```typescript
for await (const message of query({
  prompt: "Build the full authentication system with tests and documentation.",
  options: {
    allowedTools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "Task"],
    agents: {
      "implementer": {
        description: "Implements features with production-quality code",
        prompt: "You are a senior developer. Write clean, tested code.",
        tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        model: "sonnet"
      },
      "tester": {
        description: "Writes comprehensive tests for implemented features",
        prompt: "Write thorough unit and integration tests.",
        tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        model: "sonnet"
      },
      "reviewer": {
        description: "Reviews code for security, performance, and correctness",
        prompt: "Review code for vulnerabilities, edge cases, and best practices.",
        tools: ["Read", "Grep", "Glob"],
        model: "opus"
      }
    }
  }
}))
```

**Rules:**
- `Task` must be in the parent's `allowedTools` or subagents are never spawned
- Never include `Task` in a subagent's own tools — subagents cannot spawn sub-subagents
- Claude decides when to parallelize — you define capability, not scheduling
- Each subagent gets its own isolated context window

### Session Persistence & Resumption

Capture `session_id` from the init message, pass it back as `resume`:

```typescript
let sessionId: string;

// Phase 1: Read-only analysis
for await (const msg of query({
  prompt: "Analyze this codebase for security issues.",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if (msg.type === "system" && msg.subtype === "init") sessionId = msg.session_id;
  if (msg.type === "result") console.log(msg.result);
}

// Phase 2: Fix with write access (same context)
for await (const msg of query({
  prompt: "Now fix those issues.",
  options: {
    resume: sessionId,
    allowedTools: ["Read", "Edit", "Write"],
    permissionMode: "acceptEdits",
  }
})) {
  if (msg.type === "result") console.log(msg.result);
}
```

Use `forkSession` to branch from an existing session for trying different approaches.

### Streaming Message Types

| Message Type | Subtype | Content |
|-------------|---------|---------|
| `system` | `init` | Session started — contains `session_id` |
| `assistant` | — | Streaming text from the agent |
| `tool` | — | Tool call with `tool_name` and content |
| `result` | `success` | Task completed — contains `result`, `total_cost_usd` |
| `result` | `error` | Task failed — contains error details |

### Key Options

| Option | Purpose |
|--------|---------|
| `model` | Model to use (`sonnet`, `opus`, `haiku`) |
| `allowedTools` | List of tool names the agent can use |
| `permissionMode` | `"acceptEdits"` for auto-approve, or interactive |
| `maxTurns` | Maximum agent turns before stopping |
| `max_budget_usd` | Cost cap for the session |
| `cwd` | Working directory for the agent |
| `resume` | Session ID to continue from |
| `agents` | Subagent definitions (name → config) |
| `systemPrompt` | Override the system prompt |

### Go Integration Pattern

Since the Claude Agent SDK is TypeScript/Python, integrate from Go via a thin bridge subprocess:

```go
// Option A: TypeScript bridge
cmd := exec.CommandContext(ctx, "node", "agent-bridge.js")
cmd.Dir = workspacePath
// Same JSONL-over-stdio pattern as Codex app-server

// Option B: Python bridge  
cmd := exec.CommandContext(ctx, "python3", "agent_bridge.py")
```

The bridge script wraps `query()` and emits structured JSONL events on stdout, accepts commands on stdin. This gives Go the same integration shape as the Codex app-server.

---

## Comparison

| Feature | Codex App-Server | Claude Agent SDK |
|---------|-----------------|------------------|
| Language | Any (stdio protocol) | TypeScript / Python |
| Models | OpenAI (GPT-5.x) | Claude (Sonnet/Opus/Haiku) |
| Transport | stdio JSONL or WebSocket | Async generator |
| Subagents | TOML in `.codex/agents/`, built-in agents, CSV fan-out | `.claude/agents/*.md`, `Task` tool in `allowedTools` |
| Session management | thread/resume, thread/fork | `resume` session_id, `forkSession` |
| Streaming | JSONL notifications | Async iterator messages |
| Tool definition | Internal to Codex | String names (14+ built-in) |
| MCP support | Yes | Yes |
| Sandbox | Built-in sandbox modes | Via `permissionMode` |
| Cost tracking | Token counts in events | `total_cost_usd` on result |
| Context compaction | thread/compact/start | Automatic when approaching limits |
| From Go | Direct (subprocess + JSONL) | Via bridge subprocess |

## When to Use Which

**Use Codex App-Server when:**
- Building from Go or other non-JS/Python languages
- Need fine-grained control over thread lifecycle (resume, fork, rollback, compact)
- Want the richest protocol surface (40+ methods)
- Using OpenAI models

**Use Claude Agent SDK when:**
- Want the simplest API for full agentic coding
- Need explicit subagent orchestration with role definitions
- Want session persistence with read→write phase patterns
- Using Claude models
- Building in TypeScript or Python directly

**Use both when:**
- Building a multi-provider dispatch system (like Perch)
- Want to offer model choice per project/task
