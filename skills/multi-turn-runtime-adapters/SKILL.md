---
name: multi-turn-runtime-adapters
description: Adapt AI agent runtimes (Claude Code SDK, Codex CLI app-server) into multi-turn conversational systems. Covers session lifecycle, resume/fork, event normalization, JSON-RPC 2.0 over stdio, tool policy enforcement, and rich component rendering (agent→UI generative components, UI→agent bidirectional state, component registries, surface targets). Use when building orchestrators, chat UIs, or sidecar processes that need persistent multi-turn agent sessions with rich interactive interfaces.
metadata:
  author: marcus-vorwaller
  version: "1.0"
---

# Multi-Turn Runtime Adapters

You are building an **adapter layer** that wraps AI agent runtimes (Claude Code SDK, Codex CLI) into multi-turn conversational systems. Each runtime has a different interface, but they can be normalized into a common event model with a shared session lifecycle.

The goal: maintain persistent agent sessions where users can send multiple messages, resume conversations, fork threads, and receive streaming events -- all through a uniform interface regardless of the underlying runtime.

---

## When to use this skill

Use this skill when the user asks for:

- Multi-turn agent sessions with Claude Code SDK or Codex CLI
- Building a sidecar/backend that wraps agent runtimes behind an HTTP or WebSocket API
- Normalizing events from different agent runtimes into a common model
- Session resume, fork, or archive functionality
- JSON-RPC 2.0 client implementation over stdio
- Tool policy enforcement for sandboxed agent sessions
- Rich component rendering in agent chat (generative UI)
- Bidirectional agent↔UI state synchronization
- Component registry patterns for mapping tool calls to UI
- Rendering agent-driven components outside the chat bubble (sidebars, panels, canvases)

Do **not** use this skill for:

- One-shot agent invocations (just use `query()` or `codex exec` directly)
- Building the agent runtimes themselves

---

## Architecture overview

```
 User/Frontend
      |
      v
 HTTP/SSE Server (sidecar)
      |
      +---> Claude Runtime Adapter  ---> @anthropic-ai/claude-code SDK (in-process)
      |
      +---> Codex Runtime Adapter   ---> codex app-server (child process, JSON-RPC over stdio)
      |
      v
 Normalized Event Stream
 { type, data, ts }
```

Each adapter implements the same interface:

```
createSession(id, params)    -> { id }
sendMessage(id, message)     -> async (streams events)
stopTurn(id)                 -> void
resumeSession(id, params)    -> { id }
archiveSession(id)           -> void
addEventListener(id, fn)     -> removeListener()
getSession(id)               -> session info | null
capabilities                 -> { multi_turn_single_process, session_resume, ... }
```

---

## Normalized event model

All runtimes emit events through a common schema:

```js
{
  type: string,    // Event type constant
  data: object,    // Event-specific payload
  ts: string,      // ISO 8601 timestamp
}
```

### Event types

| Event | Description | Key data fields |
|-------|-------------|-----------------|
| `session_ready` | Session created or resumed | `session_id`, `runtime`, `provider_session_id?`, `resumed?` |
| `delta` | Streaming text chunk | `text` |
| `thinking` | Reasoning/thinking text | `text`, `done?` |
| `tool_start` | Tool invocation started | `tool_use_id`, `tool`, `input?`, `command?`, `file_path?`, `pattern?`, `search_path?`, `is_file_read?` |
| `tool_result` | Tool invocation completed | `tool_use_id`, `output`, `is_error`, `exit_code?`, `file_path?`, `is_file_read?` |
| `permission_request` | Agent needs permission | `tool_name`, `tool_input` |
| `permission_resolved` | Permission granted/denied | `tool_name`, `allowed` |
| `result` | Final agent response text | `text` |
| `done` | Turn complete | `stopped?`, `exit_code?` |
| `error` | Error occurred | `message`, `code?` |

### Event creation helper

```js
export const EventTypes = {
  SESSION_READY: 'session_ready',
  DELTA: 'delta',
  THINKING: 'thinking',
  TOOL_START: 'tool_start',
  TOOL_RESULT: 'tool_result',
  PERMISSION_REQUEST: 'permission_request',
  PERMISSION_RESOLVED: 'permission_resolved',
  RESULT: 'result',
  DONE: 'done',
  ERROR: 'error',
};

export function createEvent(type, data = {}) {
  return { type, data, ts: new Date().toISOString() };
}
```

---

## Runtime 1: Claude Code SDK

The `@anthropic-ai/claude-code` SDK provides an in-process async generator interface. Multi-turn is achieved through the `resume` option, which passes the provider session ID back to the SDK.

### Key SDK types

```ts
// The main entry point
function query({ prompt, options }): Query  // AsyncGenerator<SDKMessage>

// Options (subset relevant to multi-turn)
type Options = {
  resume?: string;              // Provider session ID for resume
  resumeSessionAt?: string;     // Resume from specific message ID
  forkSession?: boolean;        // Fork to new session instead of continuing
  customSystemPrompt?: string;  // Override system prompt
  appendSystemPrompt?: string;  // Append to system prompt
  abortController?: AbortController;
  maxTurns?: number;
  canUseTool?: CanUseTool;      // Tool permission callback
  cwd?: string;
  permissionMode?: 'default' | 'acceptEdits' | 'bypassPermissions' | 'plan';
  model?: string;
  mcpServers?: Record<string, McpServerConfig>;
  hooks?: Partial<Record<HookEvent, HookCallbackMatcher[]>>;
}
```

### SDK message types

The `query()` generator yields these message types:

```ts
type SDKMessage =
  | SDKSystemMessage       // type: 'system', subtype: 'init' -- first message, contains session_id
  | SDKAssistantMessage    // type: 'assistant' -- contains content blocks
  | SDKUserMessage         // type: 'user' -- tool results as user messages
  | SDKResultMessage       // type: 'result' -- final result with cost/usage
  | SDKPartialAssistantMessage  // type: 'stream_event' -- raw stream events
  | SDKCompactBoundaryMessage   // type: 'system', subtype: 'compact_boundary'
```

### The init message and session ID capture

The very first message from `query()` is a system init message containing the provider session ID. **You must capture this** to enable resume on subsequent turns.

```ts
type SDKSystemMessage = {
  type: 'system';
  subtype: 'init';
  session_id: string;     // <-- THIS is the provider session ID for resume
  tools: string[];
  model: string;
  permissionMode: PermissionMode;
  mcp_servers: { name: string; status: string }[];
  apiKeySource: ApiKeySource;
  cwd: string;
  // ...
}
```

### Multi-turn session lifecycle

```
Turn 1: query({ prompt: "Hello", options: {} })
  -> yields { type: 'system', subtype: 'init', session_id: 'abc-123' }
  -> yields assistant messages, tool use, etc.
  -> yields { type: 'result', ... }
  ** Store session_id = 'abc-123' **

Turn 2: query({ prompt: "Follow up", options: { resume: 'abc-123' } })
  -> yields { type: 'system', subtype: 'init', session_id: 'abc-123' }
  -> conversation continues with full context
  -> yields { type: 'result', ... }

Turn N: query({ prompt: "...", options: { resume: 'abc-123' } })
  -> same pattern
```

### Complete Claude adapter implementation

```js
import { query } from '@anthropic-ai/claude-code';

const sessions = new Map();

export function createSession(sessionId, params) {
  const session = {
    id: sessionId,
    status: 'active',
    conversationId: null,   // Provider session ID, captured from init message
    listeners: [],
    abortController: null,
    systemPrompt: params.systemPrompt || '',
    workingDir: params.workingDir || '',
  };
  sessions.set(sessionId, session);
  emit(session, 'session_ready', { session_id: sessionId, runtime: 'claude' });
  return { id: sessionId };
}

export async function sendMessage(sessionId, message) {
  const session = sessions.get(sessionId);
  if (!session) throw new Error(`Session not found: ${sessionId}`);

  session.abortController = new AbortController();

  const queryOptions = {
    customSystemPrompt: session.systemPrompt,
    abortController: session.abortController,
    maxTurns: 30,
    canUseTool: async (toolName, input) => {
      // Implement your tool policy here
      return { behavior: 'allow', updatedInput: input ?? {} };
    },
  };

  // Resume if we have a provider session ID from a previous turn
  if (session.conversationId) {
    queryOptions.resume = session.conversationId;
  }

  if (session.workingDir) {
    queryOptions.cwd = session.workingDir;
  }

  try {
    const stream = query({ prompt: message, options: queryOptions });

    for await (const msg of stream) {
      processMessage(session, msg);
    }

    emit(session, 'done', {});
  } catch (err) {
    if (err.name === 'AbortError' || session.abortController?.signal?.aborted) {
      emit(session, 'done', { stopped: true });
    } else {
      emit(session, 'error', { message: err.message });
    }
  } finally {
    session.abortController = null;
  }
}

function processMessage(session, msg) {
  switch (msg.type) {
    case 'system':
      if (msg.subtype === 'init' && msg.session_id) {
        // Capture the provider session ID for future resume calls
        session.conversationId = msg.session_id;
        emit(session, 'session_ready', {
          session_id: session.id,
          provider_session_id: msg.session_id,
        });
      }
      break;

    case 'assistant': {
      const content = msg.message?.content || [];
      for (const block of Array.isArray(content) ? content : [content]) {
        if (block.type === 'text') {
          emit(session, 'delta', { text: block.text });
        } else if (block.type === 'thinking') {
          emit(session, 'thinking', { text: block.thinking || block.text });
        } else if (block.type === 'tool_use') {
          // Extract structured fields from input for file-oriented tools
          // so consumers can display file_path, pattern etc. without parsing input
          const toolData = {
            tool_use_id: block.id,
            tool: block.name,
            input: block.input,
          };
          if (block.input && typeof block.input === 'object') {
            if (block.input.file_path) toolData.file_path = block.input.file_path;
            if (block.input.command) toolData.command = block.input.command;
            if (block.input.pattern) toolData.pattern = block.input.pattern;
            if (block.input.path) toolData.search_path = block.input.path;
          }
          emit(session, 'tool_start', toolData);
        }
      }
      break;
    }

    case 'user': {
      // User messages contain tool results
      const content = msg.message?.content || [];
      for (const block of Array.isArray(content) ? content : [content]) {
        if (block?.type === 'tool_result') {
          emit(session, 'tool_result', {
            tool_use_id: block.tool_use_id,
            output: block.content,
            is_error: block.is_error || false,
          });
        }
      }
      break;
    }

    case 'result':
      if (msg.result) {
        emit(session, 'result', { text: msg.result });
      }
      break;
  }
}

export function stopTurn(sessionId) {
  const session = sessions.get(sessionId);
  if (session?.abortController) {
    session.abortController.abort();
  }
}

export function resumeSession(sessionId, params) {
  const existing = sessions.get(sessionId);
  if (existing) {
    existing.status = 'active';
    if (params.providerSessionId) {
      existing.conversationId = params.providerSessionId;
    }
    emit(existing, 'session_ready', { session_id: sessionId, resumed: true });
    return { id: sessionId };
  }
  return createSession(sessionId, params);
}

export function archiveSession(sessionId) {
  const session = sessions.get(sessionId);
  if (session) {
    if (session.abortController) session.abortController.abort();
    session.status = 'archived';
    session.listeners = [];
    sessions.delete(sessionId);
  }
}

export const capabilities = {
  multi_turn_single_process: true,   // SDK keeps context in memory
  interactive_permissions: true,     // canUseTool callback
  tool_use_events: true,
  session_resume: true,              // resume option on query()
  reasoning_stream: true,            // thinking blocks
};
```

### Tool permission callback

The `canUseTool` callback is called before each tool invocation. Return `allow` or `deny`:

```js
canUseTool: async (toolName, input, { signal, suggestions }) => {
  // Allow with original input
  return { behavior: 'allow', updatedInput: input ?? {} };

  // Deny with reason
  return { behavior: 'deny', message: 'Not allowed by policy' };

  // Deny and stop the agent
  return { behavior: 'deny', message: 'Blocked', interrupt: true };
}
```

### Hooks for session events

The SDK supports hooks for lifecycle events:

```js
const options = {
  hooks: {
    SessionStart: [{
      hooks: [async (input, toolUseID, { signal }) => {
        // input.session_id, input.cwd, input.source ('startup'|'resume'|'clear'|'compact')
        return { continue: true };
      }]
    }],
    PreToolUse: [{
      matcher: 'Bash',  // optional: only match specific tools
      hooks: [async (input, toolUseID, { signal }) => {
        // input.tool_name, input.tool_input
        return { decision: 'approve' };
        // or: { decision: 'block', reason: '...' }
      }]
    }],
  }
};
```

### Using prompt as AsyncIterable for streaming input

For advanced use cases, the prompt can be an `AsyncIterable<SDKUserMessage>` instead of a string:

```js
async function* userMessages() {
  yield {
    type: 'user',
    session_id: 'session-123',
    message: { role: 'user', content: [{ type: 'text', text: 'Hello' }] },
    parent_tool_use_id: null,  // Non-null when message is from a sub-agent — see "Sub-agent event normalization"
  };
  // Yield more messages as user sends them...
}

const stream = query({ prompt: userMessages(), options: { resume: sessionId } });
```

---

## Runtime 2: Codex CLI app-server

Codex CLI provides `codex app-server`, a long-running process that communicates via JSON-RPC 2.0 over stdio. This is the preferred integration path for multi-turn Codex sessions. A single app-server process manages multiple threads with full persistence.

### Starting the app-server

```js
import { spawn } from 'node:child_process';

const child = spawn('codex', ['app-server', '--listen', 'stdio://'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: { ...process.env },
});
```

Transport options:
- `stdio://` (default) -- JSON-RPC over stdin/stdout
- `ws://IP:PORT` -- WebSocket transport

### JSON-RPC 2.0 protocol

All communication follows JSON-RPC 2.0. Messages are newline-delimited JSON on stdio.

**Request** (client to server):
```json
{ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": { ... } }
```

**Response** (server to client):
```json
{ "jsonrpc": "2.0", "id": 1, "result": { ... } }
```

**Notification** (server to client, no id):
```json
{ "jsonrpc": "2.0", "method": "turn/completed", "params": { ... } }
```

**Error response**:
```json
{ "jsonrpc": "2.0", "id": 1, "error": { "code": -32600, "message": "..." } }
```

### Initialization handshake

Before any other requests, perform the initialization handshake:

```
Client -> Server:
{ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "clientInfo": { "name": "my-app", "version": "1.0.0" }
  }
}
NOTE: clientInfo is REQUIRED. Omitting it causes: "Invalid request: missing field `clientInfo`"

Server -> Client:
{ "jsonrpc": "2.0", "id": 1, "result": { ... } }

Client -> Server (notification, no id):
{ "jsonrpc": "2.0", "method": "initialized" }
```

The `initialized` notification tells the server the client is ready for normal operation.

### Thread lifecycle

Threads are Codex's unit of conversation. Each thread has an ID, working directory, and history of turns.

#### Start a new thread

```json
// Request
{ "jsonrpc": "2.0", "id": 2, "method": "thread/start", "params": {
    "cwd": "/path/to/project",
    "approvalPolicy": "never",
    "sandbox": "danger-full-access",
    "developerInstructions": "You are a planning agent..."
  }
}

// Response -- thread is NESTED under result.thread (not result directly)
{ "jsonrpc": "2.0", "id": 2, "result": {
    "approvalPolicy": "never",
    "cwd": "/path/to/project",
    "model": "o3",
    "modelProvider": "openai",
    "sandbox": { "type": "dangerFullAccess" },
    "thread": {
      "id": "thread_abc123",
      "cwd": "/path/to/project",
      "createdAt": 1710000000,
      "updatedAt": 1710000000,
      "preview": "",
      "source": "app-server",
      "turns": []
    }
  }
}
IMPORTANT: Thread ID is at result.thread.id, NOT result.id

// Server notification follows
{ "jsonrpc": "2.0", "method": "thread/started", "params": {
    "thread": { ... }
  }
}
```

#### Resume a thread

```json
{ "jsonrpc": "2.0", "id": 3, "method": "thread/resume", "params": {
    "threadId": "thread_abc123",
    "developerInstructions": "Updated instructions...",
    "approvalPolicy": "never",
    "sandbox": "danger-full-access"
  }
}
```

The response returns the full Thread including all turn history and items.

Resume supports three modes (precedence: history > path > threadId):
1. **By threadId** (preferred): load from disk by ID
2. **By path**: load from a specific file path
3. **By history**: instantiate from in-memory history

#### Fork a thread

```json
{ "jsonrpc": "2.0", "id": 4, "method": "thread/fork", "params": {
    "threadId": "thread_abc123",
    "model": "o3",
    "developerInstructions": "New instructions for fork..."
  }
}
```

Creates a new thread with the same history up to the fork point.

#### Archive/unarchive

```json
{ "jsonrpc": "2.0", "id": 5, "method": "thread/archive", "params": { "threadId": "thread_abc123" } }
{ "jsonrpc": "2.0", "id": 6, "method": "thread/unarchive", "params": { "threadId": "thread_abc123" } }
```

#### List threads

```json
{ "jsonrpc": "2.0", "id": 7, "method": "thread/list", "params": {
    "archived": false,
    "cwd": "/path/to/project",
    "limit": 20,
    "cursor": null
  }
}
```

#### Read a thread's history

```json
{ "jsonrpc": "2.0", "id": 8, "method": "thread/read", "params": {
    "threadId": "thread_abc123",
    "includeTurns": true
  }
}
```

#### Rollback turns

```json
{ "jsonrpc": "2.0", "id": 9, "method": "thread/rollback", "params": {
    "threadId": "thread_abc123",
    "numTurns": 1
  }
}
```

This modifies thread history but does NOT revert file changes. The client is responsible for reverting local changes.

#### Compact a thread

```json
{ "jsonrpc": "2.0", "id": 10, "method": "thread/compact/start", "params": {
    "threadId": "thread_abc123"
  }
}
```

### Turn lifecycle

Within a thread, each user message starts a "turn" that the agent processes.

#### Start a turn (send user message)

```json
{ "jsonrpc": "2.0", "id": 10, "method": "turn/start", "params": {
    "threadId": "thread_abc123",
    "input": [
      { "type": "text", "text": "Add error handling to the parser" }
    ],
    "model": "o3",
    "approvalPolicy": "never",
    "effort": "high"
  }
}
```

Input supports multiple types:
- `{ "type": "text", "text": "..." }` -- text message
- `{ "type": "image", "url": "https://..." }` -- image URL
- `{ "type": "localImage", "path": "/path/to/image.png" }` -- local image
- `{ "type": "file", "name": "file.txt", "path": "/path/to/file.txt" }` -- file attachment

#### Steer a turn (inject guidance mid-turn)

```json
{ "jsonrpc": "2.0", "id": 11, "method": "turn/steer", "params": {
    "threadId": "thread_abc123",
    "expectedTurnId": "turn_xyz",
    "input": [
      { "type": "text", "text": "Actually, use a different approach..." }
    ]
  }
}
```

The `expectedTurnId` must match the currently active turn.

#### Interrupt a turn

```json
{ "jsonrpc": "2.0", "id": 12, "method": "turn/interrupt", "params": {
    "threadId": "thread_abc123",
    "turnId": "turn_xyz"
  }
}
```

### Server notifications (streaming events)

During a turn, the server sends notifications for all agent activity:

#### Thread-level notifications

| Method | Description | Key params |
|--------|-------------|------------|
| `thread/started` | Thread created | `thread` |
| `thread/archived` | Thread archived | `threadId` |
| `thread/unarchived` | Thread unarchived | `threadId` |
| `thread/name/updated` | Thread renamed | `threadId`, `name` |
| `thread/tokenUsage/updated` | Token usage updated | `threadId`, usage info |
| `thread/compacted` | Thread compacted | `threadId` |

#### Turn-level notifications

| Method | Description | Key params |
|--------|-------------|------------|
| `turn/started` | Turn began | `threadId`, `turn { id, status, items }` |
| `turn/completed` | Turn finished | `threadId`, `turn { id, status, items, error? }` |
| `turn/diff/updated` | File diff updated | `threadId`, diff info |
| `turn/plan/updated` | Agent plan updated | `threadId`, plan steps |

#### Item-level notifications (streaming content)

| Method | Description | Key params |
|--------|-------------|------------|
| `item/started` | Item began | `threadId`, `turnId`, `item` |
| `item/completed` | Item finished | `threadId`, `turnId`, `item` |
| `item/agentMessage/delta` | Text delta | `threadId`, `turnId`, `itemId`, `delta` |
| `item/commandExecution/outputDelta` | Command output | `threadId`, `turnId`, `itemId`, `delta` |
| `item/fileChange/outputDelta` | File change output | `threadId`, `turnId`, `itemId`, `delta` |
| `item/reasoning/textDelta` | Reasoning text | `threadId`, `turnId`, `itemId`, `delta`, `contentIndex` |
| `item/reasoning/summaryTextDelta` | Reasoning summary | `threadId`, `turnId`, `itemId`, `delta` |
| `item/mcpToolCall/progress` | MCP tool progress | `threadId`, `turnId`, `itemId` |
| `item/plan/delta` | Plan delta | `threadId`, `turnId`, `itemId`, `delta` |

#### Item types in `item/started` and `item/completed`

The `item` field in item notifications is a `ThreadItem` with these variants:

- `{ type: "userMessage", id, content: UserInput[] }` -- user message
- `{ type: "agentMessage", id, text }` -- agent text response
- `{ type: "reasoning", id, content?, summary? }` -- reasoning/thinking
- `{ type: "commandExecution", id, command, cwd, status, exitCode?, aggregatedOutput? }` -- shell command
- `{ type: "functionCall", id, name, callId, arguments }` -- function/tool call
- `{ type: "functionCallOutput", id, callId, output }` -- function/tool result
- `{ type: "plan", id, text }` -- plan item
- `{ type: "mcpToolCall", id, serverName, toolName, arguments, output? }` -- MCP tool call

#### Server requests (approval callbacks)

The server may send requests to the client for approval:

| Method | Description |
|--------|-------------|
| `item/commandExecution/requestApproval` | Approve a shell command |
| `item/fileChange/requestApproval` | Approve a file change |
| `item/tool/requestUserInput` | Request user input for a tool |
| `item/tool/call` | Dynamic tool call |
| `applyPatchApproval` | Approve a patch application |
| `execCommandApproval` | Approve command execution |

For headless operation, set `approvalPolicy: "never"` and `sandbox: "danger-full-access"` to bypass these.

### Approval policy options

| Value | Behavior |
|-------|----------|
| `"untrusted"` | Only trusted commands (ls, cat, etc.) auto-approved |
| `"on-failure"` | Auto-approve; ask only on failure (deprecated) |
| `"on-request"` | Auto-approve; ask only when agent explicitly requests |
| `"never"` | Never ask for approval |

### Sandbox mode options

| Value | Behavior |
|-------|----------|
| `"read-only"` | Agent can only read files |
| `"workspace-write"` | Agent can write within workspace |
| `"danger-full-access"` | Full filesystem and network access |

---

## Codex exec mode (simpler, per-turn)

For simpler use cases where you do not need the app-server's thread management, `codex exec` runs a single turn in a subprocess:

```js
import { spawn } from 'node:child_process';

const child = spawn('codex', [
  'exec',
  '--json',                                    // JSON output on stdout
  '--dangerously-bypass-approvals-and-sandbox', // No approval dialogs
  '-C', '/path/to/project',                    // Working directory
  'Your prompt here',                          // Prompt as final argument
], {
  stdio: ['pipe', 'pipe', 'pipe'],
});
```

JSON events from exec mode:

| Event type | Description |
|------------|-------------|
| `item.started` | Item started (command_execution, etc.) |
| `item.completed` | Item completed with full data |
| `turn.started` | Turn started |
| `turn.completed` | Turn finished |
| `thread.started` | Thread initialized |

For multi-turn with exec mode, you must replay conversation history in the prompt since each invocation is stateless. The app-server is strongly preferred for multi-turn.

---

## JSON-RPC 2.0 client over stdio

Reusable pattern for communicating with a child process using JSON-RPC 2.0:

```js
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { createInterface } from 'node:readline';

class JsonRpcClient {
  constructor(command, args, options = {}) {
    this.pending = new Map();  // id -> { resolve, reject, timer }
    this.listeners = [];       // notification listeners
    this.nextId = 1;

    this.child = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
      ...options,
    });

    // Parse newline-delimited JSON from stdout
    this.rl = createInterface({ input: this.child.stdout });
    this.rl.on('line', (line) => this._handleLine(line));

    this.child.stderr.on('data', (chunk) => {
      // Log stderr for debugging -- not JSON-RPC
      console.error(`[${command}] ${chunk.toString()}`);
    });

    this.child.on('exit', (code) => {
      // Reject all pending requests
      for (const [id, p] of this.pending) {
        clearTimeout(p.timer);
        p.reject(new Error(`Process exited with code ${code}`));
      }
      this.pending.clear();
    });
  }

  /** Send a request and await the response. */
  async request(method, params, timeoutMs = 30000) {
    const id = this.nextId++;
    const msg = { jsonrpc: '2.0', id, method, params };

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Request ${method} timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      this.pending.set(id, { resolve, reject, timer });
      this.child.stdin.write(JSON.stringify(msg) + '\n');
    });
  }

  /** Send a notification (no response expected). */
  notify(method, params) {
    const msg = { jsonrpc: '2.0', method, params };
    this.child.stdin.write(JSON.stringify(msg) + '\n');
  }

  /** Respond to a server request (approval callbacks, etc.). */
  respond(id, result) {
    const msg = { jsonrpc: '2.0', id, result };
    this.child.stdin.write(JSON.stringify(msg) + '\n');
  }

  /** Respond to a server request with an error. */
  respondError(id, code, message) {
    const msg = { jsonrpc: '2.0', id, error: { code, message } };
    this.child.stdin.write(JSON.stringify(msg) + '\n');
  }

  /** Register a notification listener. Returns unsubscribe function. */
  onNotification(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  /** Kill the child process. */
  async destroy() {
    this.child.kill('SIGTERM');
    await new Promise((resolve) => {
      const timer = setTimeout(() => {
        this.child.kill('SIGKILL');
        resolve();
      }, 5000);
      this.child.on('exit', () => { clearTimeout(timer); resolve(); });
    });
  }

  /** @private */
  _handleLine(line) {
    if (!line.trim()) return;
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      return; // Ignore non-JSON lines
    }

    // Response to a pending request
    if ('id' in msg && msg.id !== null && this.pending.has(msg.id)) {
      const p = this.pending.get(msg.id);
      this.pending.delete(msg.id);
      clearTimeout(p.timer);

      if (msg.error) {
        p.reject(new Error(`${msg.error.message} (code: ${msg.error.code})`));
      } else {
        p.resolve(msg.result);
      }
      return;
    }

    // Server request (has id but we did not initiate it)
    if ('id' in msg && msg.id !== null && 'method' in msg) {
      for (const listener of this.listeners) {
        listener({ type: 'request', method: msg.method, params: msg.params, id: msg.id });
      }
      return;
    }

    // Notification (no id)
    if ('method' in msg && !('id' in msg && msg.id !== null)) {
      for (const listener of this.listeners) {
        listener({ type: 'notification', method: msg.method, params: msg.params });
      }
    }
  }
}
```

### Using the client with Codex app-server

```js
const client = new JsonRpcClient('codex', ['app-server', '--listen', 'stdio://']);

// Initialize
// IMPORTANT: clientInfo is required
await client.request('initialize', {
  clientInfo: { name: 'my-app', version: '1.0.0' },
});
client.notify('initialized');

// Listen for notifications
client.onNotification((msg) => {
  if (msg.type === 'notification') {
    switch (msg.method) {
      case 'item/agentMessage/delta':
        process.stdout.write(msg.params.delta);
        break;
      case 'turn/completed':
        console.log('Turn finished:', msg.params.turn.status);
        break;
      case 'item/completed':
        // IMPORTANT: Skip agent_message here — streaming deltas already
        // delivered the text. Emitting it again causes duplicate display.
        if (msg.params.item.type !== 'agent_message') {
          console.log('Item:', msg.params.item.type, msg.params.item.id);
        }
        break;
    }
  }

  // Handle approval requests
  if (msg.type === 'request') {
    if (msg.method === 'item/commandExecution/requestApproval') {
      // Auto-approve
      client.respond(msg.id, { decision: 'approve' });
    }
  }
});

// Start a thread — IMPORTANT: thread ID is at result.thread.id
const resp = await client.request('thread/start', {
  cwd: '/path/to/project',
  approvalPolicy: 'never',
  sandbox: 'danger-full-access',
  developerInstructions: 'You are a helpful assistant.',
});
const threadId = resp.thread.id;  // NOT resp.id

// Send a message (start a turn)
await client.request('turn/start', {
  threadId,
  input: [{ type: 'text', text: 'Hello, what files are in this project?' }],
});
// Events stream via notifications...

// Send follow-up message — same threadId, context is maintained
await client.request('turn/start', {
  threadId,
  input: [{ type: 'text', text: 'Now refactor the main module' }],
});

// Cleanup
await client.destroy();
```

---

## Event normalization mapping

### Claude SDK -> normalized events

| SDK message | Normalized event | Notes |
|-------------|------------------|-------|
| `{ type: 'system', subtype: 'init' }` | `session_ready` (capture `session_id`) | |
| `{ type: 'assistant' }` with text block | `delta` | |
| `{ type: 'assistant' }` with thinking block | `thinking` | |
| `{ type: 'assistant' }` with tool_use block | `tool_start` | |
| `{ type: 'user' }` with tool_result block | `tool_result` | |
| `{ type: 'result' }` | **SKIP** (don't emit delta) | Text is extracted post-loop via `extractFinalText` → `RESULT`. Emitting a `DELTA` here causes the response to appear twice. |
| Generator completes | `result` + `done` | Use `extractFinalText` on all messages, emit once |
| Generator throws AbortError | `done` (stopped) | |
| Generator throws other error | `error` | |

### Codex app-server -> normalized events

| Codex notification | Normalized event | Notes |
|--------------------|------------------|-------|
| `thread/started` | `session_ready` | |
| `turn/started` | `thinking` (empty, done: false) | Emit immediately so UI shows activity before first item arrives |
| `item/agentMessage/delta` | `delta` | Streaming text chunks |
| `item/completed` (agentMessage) | **SKIP** | Text already delivered via streaming deltas — emitting here causes duplicates |
| `item/started` (reasoning) | `thinking` (empty, done: false) | Signal that reasoning has begun, before streaming deltas |
| `item/reasoning/textDelta` | `thinking` | Streaming reasoning. **IMPORTANT**: method is `item/reasoning/textDelta` not `reasoning/textDelta` — see common issues |
| `item/reasoning/summaryTextDelta` | `thinking` | Same prefix caveat — `item/reasoning/summaryTextDelta` |
| `item/completed` (reasoning) | `thinking` (done) | Final reasoning with `done: true` |
| `item/started` (commandExecution) | `tool_start` | Classify file-read commands (cat, grep, find, etc.) with semantic `tool` name and `file_path` |
| `item/completed` (commandExecution) | `tool_result` | Same classification applied to result |
| `item/completed` (functionCall) | `tool_start` | |
| `item/completed` (functionCallOutput) | `tool_result` | |
| `turn/completed` | `done` | `result` text is typically empty for Codex — text comes via deltas |
| `error` (willRetry: false) | `error` | Skip if `willRetry: true` |

### Codex exec JSON -> normalized events

| Codex exec event | Normalized event |
|------------------|------------------|
| `{ type: 'item.started', item.type: 'command_execution' }` | `tool_start` |
| `{ type: 'item.completed', item.type: 'reasoning' }` | `thinking` |
| `{ type: 'item.completed', item.type: 'agent_message' }` | `delta` |
| `{ type: 'item.completed', item.type: 'command_execution' }` | `tool_result` |
| `{ type: 'item.completed', item.type: 'function_call' }` | `tool_start` |
| `{ type: 'item.completed', item.type: 'function_call_output' }` | `tool_result` |
| `{ type: 'turn.completed' }` | `done` |

---

## Sub-agent event normalization

When the agent spawns sub-agents (via the `Task` tool in Claude or thread delegation in Codex), their events arrive interleaved with the parent's. The key insight: **don't create separate event types** — add an optional `subagent_id` field to all existing event types and let the UI group by it.

### Claude SDK sub-agent detection

The SDK supports sub-agents natively through the `Task` built-in tool. Every message carries `parent_tool_use_id`:

- `null` → message belongs to the parent/orchestrator context
- A string → message is from a sub-agent spawned by the `tool_use` with that ID

```js
function processClaudeMessage(session, msg) {
  const subagentId = msg.parent_tool_use_id || null;

  // Helper that attaches subagent_id to every emitted event
  function emitWithContext(eventType, data) {
    if (subagentId) data.subagent_id = subagentId;
    emit(session, eventType, data);
  }

  // Detect Task tool calls — these are sub-agent spawn points
  if (msg.type === 'assistant') {
    for (const block of msg.message?.content ?? []) {
      if (block.type === 'tool_use' && block.name === 'Task') {
        emitWithContext(EventTypes.TOOL_START, {
          tool: 'Task',
          subagent_spawn: true,
          subagent_name: block.input?.agent || block.input?.description || 'sub-agent',
        });
      }
    }
  }

  // All other events use emitWithContext instead of emit
  // so subagent_id is propagated automatically
}
```

For sub-agents to work, `Task` must be in `allowedTools`:

```js
if (session.mode === 'implementation') {
  queryOptions.allowedTools = [
    'Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep',
    'Task',  // Required for sub-agent spawning
    'WebSearch', 'WebFetch',
  ];
  queryOptions.maxTurns = 100;  // Implementation needs more turns
}
```

Agent definitions are auto-discovered from `.claude/agents/*.md` in the working directory — they are NOT passed as SDK options.

### Codex app-server sub-agent detection

Codex manages sub-agents as child threads. Track the mapping on the session:

```js
// On the session object
session.subagentThreads = new Map();  // threadId → { subagentId, name }

function handleNotification(session, method, params) {
  // Detect child thread creation
  if (method === 'thread/started' && params.parent_thread_id === session.threadId) {
    session.subagentThreads.set(params.thread_id, {
      subagentId: params.agent_id || params.thread_id,
      name: params.agent_name || 'sub-agent',
    });
  }

  // Resolve subagent_id for any notification
  const subagentId = resolveSubagentId(session, params);

  function emitWithContext(eventType, data) {
    if (subagentId) data.subagent_id = subagentId;
    emit(session, eventType, data);
  }

  // ... rest of notification handling uses emitWithContext
}

function resolveSubagentId(session, params) {
  const threadId = params.thread_id || params.threadId;
  if (threadId && session.subagentThreads.has(threadId)) {
    return session.subagentThreads.get(threadId).subagentId;
  }
  if (params.agent_id && params.agent_id !== session.threadId) {
    return params.agent_id;
  }
  return null;
}
```

For implementation mode, configure thread limits:

```js
// In thread/start params for implementation mode
{
  agents: {
    max_threads: 4,  // Concurrent sub-agent cap
    max_depth: 1,    // Direct children only — prevent runaway nesting
  }
}
```

### UI: SubAgentBlock pattern

Extend the `ContentBlock` discriminated union with a `subagent` kind:

```ts
interface SubAgentState {
  id: string;             // The subagent_id
  name: string;           // Agent name/description
  status: 'running' | 'completed' | 'failed';
  toolCalls: number;
  fileChanges: number;
  blocks: ContentBlock[];  // Nested blocks — same type, recursive
  startedAt: string;
  completedAt?: string;
}

type ContentBlock =
  | { kind: 'text'; text: string }
  | { kind: 'tool'; tool: ToolEvent }
  | { kind: 'subagent'; subagent: SubAgentState }  // New
  // ... other kinds
```

Event routing in `applyEventBlocksToMessage()`:

1. When `tool_start` has `subagent_spawn: true` → create a `subagent` ContentBlock with a new SubAgentState
2. When subsequent events carry `subagent_id` → route to the matching SubAgentState's `blocks` array (reuse the same `applyEventBlocksToMessage` function recursively)
3. When `tool_result` matches the sub-agent's spawn tool_use_id → mark SubAgentState as completed
4. Events without `subagent_id` → apply to main message as before (no regression)

The SubAgentBlock component renders collapsed by default (name + summary stats) and expands to show the full nested block stream — same rendering logic as the parent chat, just indented with a left border accent.

---

## Tool event field extraction for file reads

When building UIs that display agent tool calls, file-read operations (Read, Glob, Grep for Claude; cat, grep, find for Codex) need special treatment. Without extraction, they blend into generic tool calls and users can't tell what the agent is exploring.

### Claude: extract structured fields from tool_use input

The Claude SDK emits `tool_use` blocks with an `input` object. Extract key fields to the top level of the `tool_start` event so UI consumers can display them without parsing nested input:

```js
// In the tool_use handler:
const toolData = { tool_use_id: block.id, tool: block.name, input: block.input };
if (block.input && typeof block.input === 'object') {
  if (block.input.file_path) toolData.file_path = block.input.file_path;  // Read
  if (block.input.command) toolData.command = block.input.command;          // Bash
  if (block.input.pattern) toolData.pattern = block.input.pattern;          // Glob/Grep
  if (block.input.path) toolData.search_path = block.input.path;            // Glob/Grep dir
}
emit(session, 'tool_start', toolData);
```

### Codex: classify file-reading bash commands

Codex only has `command_execution` items — file reads are indistinguishable from other bash commands. Add a classifier that detects file-read commands and emits semantic tool names:

```js
function classifyBashCommand(command) {
  if (typeof command !== 'string') return { isFileRead: false };
  const trimmed = command.trim();

  // File readers: cat, head, tail, less, stat, file, wc
  const fileReadMatch = trimmed.match(/^(cat|head|tail|less|stat|file|wc)\s+(?:-[^\s]+\s+)*(.+)$/);
  if (fileReadMatch) return { isFileRead: true, tool: fileReadMatch[1], file_path: fileReadMatch[2].trim() };

  // Search tools: grep, rg
  if (/^(grep|rg)\s+/.test(trimmed)) return { isFileRead: true, tool: trimmed.startsWith('rg') ? 'rg' : 'grep', file_path: '' };

  // Directory browsers: find, ls, tree
  const browseMatch = trimmed.match(/^(find|ls|tree)(?:\s+(.*))?$/);
  if (browseMatch) return { isFileRead: true, tool: browseMatch[1], file_path: (browseMatch[2] || '').trim() };

  return { isFileRead: false };
}

// In the item/started handler:
const classified = classifyBashCommand(params.item.command);
emit(session, 'tool_start', {
  tool_use_id: params.item.id,
  tool: classified.isFileRead ? classified.tool : 'bash',  // semantic name
  command: params.item.command,                              // full command preserved
  file_path: classified.file_path || undefined,
  is_file_read: classified.isFileRead || undefined,
});
```

### Frontend: categorize and summarize file tools

The UI needs to distinguish file-read tools from other tools for icons and summaries:

```js
const FILE_READ_COMMANDS = new Set(['cat', 'head', 'tail', 'less', 'find', 'ls', 'tree', 'stat', 'wc', 'rg']);

function toolCategory(name) {
  const lower = name.toLowerCase();
  if (lower.includes('bash') || lower.includes('shell') || lower.includes('plan')) return 'terminal';
  if (lower.includes('read') || lower.includes('file') || lower.includes('glob')
    || lower.includes('grep') || FILE_READ_COMMANDS.has(lower)) return 'file';
  if (lower.includes('code') || lower.includes('edit') || lower.includes('write')) return 'code';
  return 'other';
}
```

For collapsed tool call summaries, show the search pattern alongside counts:
- **Glob**: `"3 files  **/*.ts"` (not just `"3 files matched"`)
- **Grep**: `"12 matches  \"className\""` (not just `"12 matches"`)
- **Read**: Show the file path
- **In-progress**: Show the file path or pattern instead of generic `"Running..."`

### Frontend: fallback extraction from nested input

For backward compatibility with events persisted before the sidecar extracted fields, the frontend should fall back to extracting from the nested `input` object:

```ts
const inputObj = (data.input && typeof data.input === 'object') ? data.input : null;
const filePath = data.file_path ?? inputObj?.file_path;
const pattern = data.pattern ?? inputObj?.pattern;
```

---

## Session lifecycle patterns

### Create -> message -> message -> archive

Standard flow for a conversation:

```
createSession(id, { systemPrompt, workingDir })
  -> session_ready

sendMessage(id, "First message")
  -> session_ready (with provider_session_id)  // Claude only, on init
  -> delta, thinking, tool_start, tool_result...
  -> result
  -> done

sendMessage(id, "Follow up")
  -> delta, thinking, tool_start, tool_result...
  -> result
  -> done

archiveSession(id)
```

### Resume across process restarts

If your sidecar process restarts, you can resume sessions by storing the provider session ID:

```
// Before restart: store mapping
sessions_db.set(sessionId, { providerSessionId: session.conversationId })

// After restart: resume
const stored = sessions_db.get(sessionId)
resumeSession(sessionId, {
  providerSessionId: stored.providerSessionId,  // Claude: SDK session_id
  // or threadId for Codex app-server
})
```

For Claude, the `resume` option on `query()` tells the SDK to load the conversation from its local storage.

For Codex app-server, `thread/resume` loads the thread from disk by `threadId`.

### Fork for branching conversations

Both runtimes support creating a branch from an existing conversation:

- **Claude SDK**: `forkSession: true` with `resume` creates a new session from the existing one
- **Codex app-server**: `thread/fork` with `threadId` creates a new thread with copied history

---

## Tool policy enforcement

For sandboxed agent sessions, implement a tool policy that controls what the agent can do:

```js
// Allowed read-only shell commands
const ALLOWED_SHELL = [
  /^cat\s/, /^ls\s/, /^ls$/, /^head\s/, /^tail\s/,
  /^find\s/, /^grep\s/, /^rg\s/, /^wc\s/, /^echo\s/,
  /^pwd$/, /^which\s/, /^file\s/, /^stat\s/, /^tree/,
];

// Explicitly denied commands
const DENIED_SHELL = [
  /^rm\s/, /^sudo\s/, /^chmod\s/, /^chown\s/,
  /^git\s+push/, /^git\s+reset\s+--hard/,
  /^kill\s/, /^pkill\s/, /^shutdown/, /^reboot/,
];

// Allowed write commands (domain-specific CLI)
const ALLOWED_WRITE = [
  /^plan\s+/,  // Your domain CLI
];

function isAllowed(toolName, command) {
  if (toolName !== 'Bash') {
    // Read tools always allowed
    if (['Read', 'Glob', 'Grep'].includes(toolName)) return { allowed: true };
    // Write tools denied
    if (['Write', 'Edit'].includes(toolName)) return { allowed: false, reason: 'Writes denied' };
  }

  const trimmed = (command || '').trim();
  for (const p of DENIED_SHELL) if (p.test(trimmed)) return { allowed: false, reason: 'Denied' };
  for (const p of ALLOWED_WRITE) if (p.test(trimmed)) return { allowed: true };
  for (const p of ALLOWED_SHELL) if (p.test(trimmed)) return { allowed: true };
  return { allowed: false, reason: 'Not in allowlist' };
}

// Claude: use in canUseTool callback
canUseTool: async (toolName, input) => {
  const command = toolName === 'Bash' ? input?.command : undefined;
  const result = isAllowed(toolName, command);
  if (result.allowed) return { behavior: 'allow', updatedInput: input ?? {} };
  return { behavior: 'deny', message: result.reason };
}

// Codex: set approvalPolicy: 'never' and sandbox: 'danger-full-access'
// then rely on developerInstructions to constrain behavior
// OR implement approval callbacks via server requests
```

### Mode-aware tool policy

Real systems need multiple session modes with different capabilities. Add a `mode` parameter to the policy function:

```js
function isAllowed(toolName, command, mode) {
  if (mode === 'implementation') return isAllowedImplementation(toolName, command);
  return isAllowedPlanner(toolName, command);  // Default: read-only
}
```

Implementation mode unlocks coding tools while keeping safety rails:

```js
// Implementation mode: allows
const IMPL_ALLOWED_TOOLS = [
  'Read', 'Glob', 'Grep', 'Bash',
  'Write', 'Edit',     // File mutations — the big unlock
  'Task',              // Sub-agent spawning
  'WebSearch', 'WebFetch',
];

// Implementation mode: expanded shell allowlist
const IMPL_ALLOWED_SHELL = [
  // All read-only (same as planner) plus:
  /^git\s+(add|commit|push|pull|fetch|show|diff|log|status|stash|merge|rebase|checkout|branch|remote|rev-parse|tag|cherry-pick)\b/,
  /^(npm|npx|node|go|make|cargo|python3|pip3)\b/,  // Build/test tools
  /^(mkdir|cp|mv|rm)\s/,  // File operations (rm -rf / caught by deny)
];
```

**Security lesson — use word boundaries in deny patterns:**

When `permissionMode: 'bypassPermissions'` is set (as it should be for implementation mode — you don't want the agent stuck waiting for interactive approval), there is no interactive safety net. Start-of-string anchors (`^`) create a bypass via command chaining:

```js
// BAD: ^rm bypasses via "echo foo; rm -rf /"
const DENY_BAD  = [/^rm\s+-rf?\s+\//];

// GOOD: \b catches dangerous commands anywhere in the string
const DENY_GOOD = [/\brm\s+-rf?\s+\//];
```

This applies to all deny patterns — `sudo`, `shutdown`, `kill`, `git push --force`, etc. Always use `\b` word boundaries when the agent has `bypassPermissions`.

```js
const IMPL_DENIED = [
  /\brm\s+-rf?\s+\//,          // rm -rf /
  /\bsudo\s/,
  /\bgit\s+push\s+.*--force/,  // deny force push
  /\bgit\s+push\s+-f\b/,       // deny -f shorthand
  /\bgit\s+reset\s+--hard/,
  /\bshutdown\b/, /\breboot\b/,
  /\bkill\s/, /\bpkill\s/,
  /\bchmod\s/, /\bchown\s/,
  /\bdd\b.*\bof=/,
];
```

Wire it into Claude's `query()` call:

```js
const queryOptions = {
  canUseTool: async (toolName, input) => {
    const command = toolName === 'Bash' ? (input?.command ?? '') : undefined;
    const result = isAllowed(toolName, command, session.mode);
    if (result.allowed) return { behavior: 'allow', updatedInput: input ?? {} };
    return { behavior: 'deny', message: result.reason };
  },
};

if (session.mode === 'implementation') {
  queryOptions.permissionMode = 'bypassPermissions';
}
```

### Agent definition file management

Sub-agents require role definitions in the workspace. Claude and Codex use different formats:

| Runtime | Format | Location | Discovery |
|---------|--------|----------|-----------|
| Claude Agent SDK | Markdown (`.md`) | `{cwd}/.claude/agents/` | Auto-discovered by SDK |
| Codex app-server | TOML (`.toml`) | `{cwd}/.codex/agents/` | Loaded on startup |

**Claude agent definition** (`.claude/agents/implementer.md`):
```markdown
---
name: implementer
description: Implementation-focused agent for writing production code.
---

Write clean, tested code for the assigned task.
Follow project conventions. Commit with task ID reference.
Run existing tests to verify changes don't break anything.
```

**Codex agent definition** (`.codex/agents/implementer.toml`):
```toml
name = "implementer"
description = "Implementation-focused agent for writing production code."
model_reasoning_effort = "high"
developer_instructions = """
Write clean, tested code for the assigned task.
Follow project conventions. Commit with task ID reference.
Run existing tests to verify changes don't break anything.
"""
```

Codex required fields: `name`, `description`, `developer_instructions`. Optional: `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `nickname_candidates`.

Codex built-in agents (`default`, `worker`, `explorer`) are always available even without custom files.

**Workspace preparation pattern**: Before launching an implementation session, copy default agent templates to the workspace if they don't exist. Never overwrite — respect project customizations:

```js
import { cp, access, mkdir } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const TEMPLATES_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'templates', 'agents');

export async function prepareWorkspace(workingDir, runtime) {
  const subdir = runtime === 'codex' ? '.codex' : '.claude';
  const targetDir = join(workingDir, subdir, 'agents');
  const sourceDir = join(TEMPLATES_DIR, runtime === 'codex' ? 'codex' : 'claude');

  try { await access(sourceDir); } catch { return; }  // No templates

  await mkdir(targetDir, { recursive: true });

  const { readdir } = await import('node:fs/promises');
  for (const file of await readdir(sourceDir)) {
    const target = join(targetDir, file);
    try {
      await access(target);  // Already exists — skip
    } catch {
      await cp(join(sourceDir, file), target);
    }
  }
}
```

Call this from `createSession()` when mode is `'implementation'`, before spawning the agent process.

---

## Exposing sessions over HTTP/SSE

Wrap the adapter layer behind an HTTP server for frontend consumption:

```
POST   /sessions              - Create session (body: session_id, runtime, params)
POST   /sessions/:id/message  - Send message (body: message, node_context?)
POST   /sessions/:id/stop     - Stop current turn
POST   /sessions/:id/resume   - Resume session (body: provider_session_id?)
DELETE /sessions/:id           - Archive session
GET    /sessions/:id/events   - SSE stream
GET    /health                 - Health check
```

### SSE stream implementation

```js
// GET /sessions/:id/events
app.get('/sessions/:id/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',
  });
  res.write(': connected\n\n');

  const removeListener = runtime.addEventListener(req.params.id, (event) => {
    res.write(`event: ${event.type}\n`);
    res.write(`data: ${JSON.stringify(event)}\n\n`);
  });

  // Heartbeat every 15s
  const heartbeat = setInterval(() => res.write(': heartbeat\n\n'), 15000);

  req.on('close', () => {
    clearInterval(heartbeat);
    removeListener();
  });
});
```

### Async message handling

Messages should be accepted immediately and processed asynchronously:

```js
// POST /sessions/:id/message
app.post('/sessions/:id/message', async (req, res) => {
  const { message, runtime: runtimeName } = req.body;
  res.status(202).json({ ok: true, accepted: true });

  // Process asynchronously -- events flow through SSE
  try {
    const rt = getRuntime(runtimeName);
    await rt.sendMessage(req.params.id, message);
  } catch (err) {
    console.error('sendMessage error:', err.message);
  }
});
```

---

## Runtime capability comparison

| Capability | Claude Code SDK | Codex app-server | Codex exec |
|------------|----------------|-----------------|------------|
| Multi-turn (single process) | Yes (resume) | Yes (threads) | No (per-invocation) |
| Session resume across restarts | Yes (session_id) | Yes (threadId) | No |
| Thread fork/branch | Yes (forkSession) | Yes (thread/fork) | No |
| Thread rollback | No | Yes (thread/rollback) | No |
| Thread compact | No | Yes (thread/compact/start) | No |
| Streaming deltas | Yes | Yes | Limited |
| Reasoning/thinking stream | Yes | Yes | Yes (item.completed) |
| Interactive permissions | Yes (canUseTool) | Yes (approval requests) | No |
| Tool use events | Yes | Yes | Yes |
| MCP server support | Yes | Yes | Unknown |
| Mid-turn steering | No | Yes (turn/steer) | No |

---

## Best practices

### Do

- **Capture the provider session ID immediately** from the first system/init message (Claude) or thread/start response (Codex)
- **Store provider session IDs persistently** so sessions can be resumed after sidecar restarts
- **Normalize events early** in the adapter layer so consumers do not need to know which runtime is active
- **Set timeouts on JSON-RPC requests** since child processes can hang
- **Use AbortController for Claude** and turn/interrupt for Codex to stop runaway agents
- **Heartbeat SSE connections** to detect stale clients (every 15s is a good interval)
- **Accept messages with 202** and process asynchronously -- never block the HTTP response on agent completion
- **Log stderr from child processes** for debugging -- it is not part of the JSON-RPC protocol

### Don't

- **Don't replay conversation history manually** when the runtime supports resume natively (Claude `resume`, Codex `thread/resume`)
- **Don't mix JSON-RPC requests and notifications** -- requests have `id` fields and expect responses; notifications do not
- **Don't forget the `initialized` notification** after the Codex app-server `initialize` response
- **Don't assume event ordering** -- tool_start for one tool may arrive before tool_result for a previous one
- **Don't hardcode the runtime** -- use the adapter interface so you can switch between Claude and Codex
- **Don't kill child processes without SIGTERM first** -- give them a chance to clean up, then SIGKILL after a timeout
- **Don't persist raw SDK/Codex events** -- normalize them first so your storage format is runtime-agnostic

---

## Common issues

### Issue: Claude resume fails silently

**Symptom**: Passing `resume` option but getting a fresh conversation.

**Cause**: The session ID expired or was cleaned up by the SDK. Claude Code stores sessions locally with TTL.

**Solution**: Check that `session_id` from the init message matches what you stored. Fall back to a new session gracefully.

### Issue: Codex app-server does not respond

**Symptom**: JSON-RPC requests hang forever.

**Cause**: Missing `initialized` notification after `initialize` response, or the process crashed (check stderr).

**Solution**: Always send `{ "jsonrpc": "2.0", "method": "initialized" }` after the initialize response. Set request timeouts.

### Issue: Events arrive after done/completed

**Symptom**: Receiving delta events after the turn/completed notification.

**Cause**: Buffering in the stdio pipe or race condition in event dispatch.

**Solution**: Buffer events and process them in order. Consider the `turn/completed` notification as the definitive end marker.

### Issue: Tool results not correlated to tool starts

**Symptom**: Cannot match which `tool_result` belongs to which `tool_start`.

**Cause**: Using different ID fields between events.

**Solution**: For Claude, use `block.id` from `tool_use` blocks and `block.tool_use_id` from `tool_result` blocks. For Codex, use `item.id` consistently.

### Issue: Codex initialize fails with "missing field clientInfo"

**Symptom**: `initialize({})` returns JSON-RPC error -32600.

**Cause**: The `clientInfo` field is required, not optional.

**Solution**: Always pass `{ clientInfo: { name: 'your-app', version: '1.0.0' } }` in the initialize params.

### Issue: Codex turn/start fails with "invalid type: null, expected a string"

**Symptom**: First `turn/start` after `thread/start` fails.

**Cause**: Extracting thread ID from wrong field. The `thread/start` response nests the thread under `result.thread`, not at the result root.

**Solution**: Use `response.thread.id`, not `response.id`.

### Issue: Agent text appears as multiple chat bubbles instead of one

**Symptom**: Streaming deltas render as separate messages in the UI, or the final text appears twice.

**Cause**: Two problems:
1. **Double-emit**: Both streaming deltas (`item/agentMessage/delta`) AND the completion event (`item/completed` for `agent_message`) emit the same text. The completion event has the full accumulated text, so it duplicates everything the deltas already delivered.
2. **Event ordering on replay**: When persisting events to a database, if `created_at` uses second-precision `datetime('now')`, events within the same second get ordered by row ID. Since SSE events are persisted asynchronously, they can arrive out of order — a `done` event may be stored between two `delta` events, causing the replay to split them into separate messages.

**Solution**:
1. **Skip `item/completed` for `agent_message`** — the streaming deltas already delivered the text. Only use `item/completed` for non-streamed item types (reasoning, command_execution, function_call).
2. **Use the event's own timestamp for storage** — sidecar events include a `ts` field with millisecond precision. Extract it and use it as `created_at` instead of `datetime('now')`. This guarantees correct replay ordering.
3. **Same pattern for Claude**: The SDK's `result` message type should NOT emit a `DELTA` event — only emit `RESULT` after the stream completes. Otherwise the final text appears twice.

### Issue: Scrambled/garbled text on historical session replay

**Symptom**: When viewing a saved session from history, the agent's text has words and token fragments in the wrong order. For example, what should be `Using perch-planner first because this is a planning request` renders as `Using perch-pl anner this is first a because,ch plan request`. Inline code backticks are split across wrong positions. The text looks corrupted.

**Cause**: Millisecond-precision timestamps are **not sufficient** for token-level streaming deltas. LLM APIs stream tokens faster than 1ms apart — 5-10 delta events can share the same millisecond timestamp. When the `ORDER BY` falls back to the tiebreaker column and that column is a random UUID (v4), the tokens within each millisecond group are reassembled in random order.

Real example from a Codex session (note the timestamps):
```
seq 10  delta " first"    2026-03-16 15:47:38.086
seq 11  delta " because"  2026-03-16 15:47:38.086
seq 12  delta " this"     2026-03-16 15:47:38.086
seq 13  delta " is"       2026-03-16 15:47:38.086
seq 14  delta " a"        2026-03-16 15:47:38.086
```

Five tokens at the same millisecond. With `ORDER BY created_at, id` (random UUID), these could come back in any order: `" this is first a because"` instead of `" first because this is a"`.

**Solution**: Add a monotonically increasing `seq` column per session:

```sql
-- Migration: add seq column with backfill from insertion order
ALTER TABLE session_events ADD COLUMN seq INTEGER NOT NULL DEFAULT 0;

-- Backfill existing events using rowid (SQLite preserves insertion order)
UPDATE session_events
SET seq = (
    SELECT COUNT(*)
    FROM session_events AS e2
    WHERE e2.session_id = session_events.session_id
      AND e2.rowid < session_events.rowid
) + 1;

CREATE INDEX idx_session_events_order ON session_events(session_id, created_at, seq);
```

On insert, compute the next sequence number:
```go
var nextSeq int
tx.QueryRow(
    `SELECT COALESCE(MAX(seq), 0) + 1 FROM session_events WHERE session_id = ?`,
    sessionID,
).Scan(&nextSeq)

tx.Exec(
    `INSERT INTO session_events (id, session_id, event_type, payload_json, created_at, seq)
     VALUES (?, ?, ?, ?, ?, ?)`,
    newID(), sessionID, eventType, payload, eventTime, nextSeq,
)
```

All queries must use `ORDER BY created_at, seq` (not `created_at, id`):
```sql
-- GOOD: deterministic insertion-order replay
SELECT * FROM session_events WHERE session_id = ? ORDER BY created_at, seq

-- BAD: random order within same millisecond
SELECT * FROM session_events WHERE session_id = ? ORDER BY created_at, id
```

**Why not use ULIDs or UUID v7?** Those are time-sortable but still only have millisecond resolution. With 5-10 events per millisecond, you'd get the same collisions. A simple integer sequence is the only reliable tiebreaker.

**Why not microsecond timestamps?** The timestamps come from the sidecar (Node.js), which only provides millisecond precision via `Date.now()`. Even with microsecond precision, you'd need the sequence number as a safety net — clock skew and batching can still produce ties.

### Issue: Agent text renders as one giant paragraph (wall of text)

**Symptom**: After a multi-tool turn completes, all the agent's text is concatenated into a single paragraph with no line breaks. Markdown formatting (inline code, links) renders correctly, but there are no paragraph breaks between what should be separate sections.

**Cause**: In a multi-turn loop, the agent emits text, calls tools, then emits more text. Each segment arrives as `delta` events that get concatenated with `+=`. The text from before and after tool calls runs together: `"...seams in the code.The key seams are showing up..."`.

**Solution**: Track `hadToolSinceLastDelta` and insert `\n\n` paragraph breaks when a delta arrives after a tool event. See "Paragraph separators between tool calls" in the Chat UI rendering section. Both the live streaming path and the history replay path need this logic.

### Issue: sendMessage hangs forever if app-server dies

**Symptom**: `sendMessage` never resolves after app-server process crashes.

**Cause**: The `waitForTurnComplete` promise is only resolved by the `turn/completed` notification handler. If the process dies without emitting that notification, the promise leaks.

**Solution**: In the child process `close` event handler, check for and resolve any pending turn promise:
```js
child.on('close', (code) => {
  // ... cleanup rpcClient, appServer ...
  if (session._turnResolve) {
    session._turnResolve();
    session._turnResolve = null;
  }
});
```

### Issue: Codex reasoning/thinking events silently dropped

**Symptom**: The UI never shows "Thinking" during Codex sessions. The agent appears idle for long periods then suddenly a block of text appears. Claude sessions show thinking correctly.

**Cause**: The Codex app-server notification methods for reasoning events are prefixed with `item/` — the full method names are `item/reasoning/textDelta` and `item/reasoning/summaryTextDelta`. If your adapter's switch/case listens for `reasoning/textDelta` (without the `item/` prefix), the events silently fall through to the default case and are never processed.

This is easy to miss because:
1. The server notification table in the Codex docs lists these under "Item-level notifications" but doesn't always emphasize the `item/` prefix
2. Other item-level methods (`item/agentMessage/delta`, `item/started`, `item/completed`) are obviously prefixed because their names start differently
3. `reasoning/textDelta` looks like a plausible method name, and there's no runtime error — JSON-RPC notifications with unrecognized methods are silently ignored

**Solution**: Use the full `item/`-prefixed method names. For safety, handle both variants:
```js
case 'item/reasoning/textDelta':
case 'item/reasoning/summaryTextDelta':
case 'reasoning/textDelta':        // fallback for protocol variations
case 'reasoning/summaryTextDelta':  // fallback for protocol variations
  if (params.delta) {
    emitWithContext(EventTypes.THINKING, { text: params.delta });
  }
  break;
```

### Issue: No activity indication between turn/start and first item event

**Symptom**: After the user sends a message, the UI shows a generic "Working" status (or nothing) for several seconds before the first streaming event arrives. Particularly noticeable with Codex where the model may reason internally before emitting any items.

**Cause**: The `turn/started` notification (emitted when the agent begins processing) and `item/started` with type `reasoning` (emitted when a reasoning item starts) are typically handled as no-ops. The UI only transitions to "Thinking" or "Running tool" when `delta`, `thinking`, or `tool_start` events arrive — but there's a gap between the turn starting and the first such event.

**Solution**: Emit an empty `thinking` event on both `turn/started` and `item/started` (reasoning) to give immediate UI feedback:
```js
case 'turn/started':
  // Immediate activity signal before any items arrive
  emitWithContext(EventTypes.THINKING, { text: '', done: false });
  break;

case 'item/started':
  if (params.item?.type === 'command_execution') {
    // ... existing tool_start handling ...
  } else if (params.item?.type === 'reasoning') {
    // Signal thinking before streaming reasoning deltas arrive
    emitWithContext(EventTypes.THINKING, { text: '', done: false });
  }
  break;
```

The empty `text: ''` is fine — the UI's thinking state is triggered by the event type, not the content. The `done: false` keeps the thinking indicator active until reasoning completes or another event supersedes it.

### Issue: UI status indicator shows generic "Responding" instead of granular activity

**Symptom**: The chat header shows "Responding" for all agent activity (thinking, tool execution, text generation). Users can't tell whether the agent is reasoning, running a command, or writing a reply.

**Cause**: The UI reads the coarse `sessionStatus` ('idle' | 'responding' | 'error' | 'initializing') for its status display, ignoring the granular `activeAgentActivity` computed property that already tracks the specific activity kind (thinking, tool, responding, permission) with a human-readable label and appropriate icon.

**Solution**: Wire the granular activity status into the UI. The store already computes detailed activity via priority-based checks (pending permissions → running tools → streaming text → thinking → fallback). The UI just needs to read it:
```js
// Instead of:
let status = $derived(store.sessionStatus);
let statusLabel = status === 'responding' ? 'Responding' : 'Ready';

// Use:
let activity = $derived(store.activeAgentActivity);
let statusLabel = activity.busy ? activity.label : 'Ready';
// activity.label is "Thinking", "Running Bash", "Writing reply",
// "Waiting for approval", "Working", etc.
```

This requires no new UI components — just replace the data source for the existing indicator text.

---

## Chat UI rendering: the accumulation pattern

When building a chat UI that renders streaming agent events, the key challenge is accumulating deltas into a single message bubble. Here's the pattern that works:

### Data model

```js
{
  id: string,
  role: 'user' | 'agent' | 'system',
  content: string,        // Accumulated text from delta events
  thinking: { content: string, done: boolean },
  toolEvents: ToolEvent[],
  done: boolean,           // True when turn is complete
}
```

### Accumulation rules

1. **`thinking`** → create agent message if none exists, append to `thinking.content`
2. **`delta`** → create agent message if none exists, append to `content` (see paragraph separator below)
3. **`tool_start`** → set `hadToolSinceLastDelta = true`, append to `toolEvents` array
4. **`tool_result`** → find matching `tool_start` and upgrade it
5. **`result`** → set `content` if empty (fallback), mark `done: true`, reset `hadToolSinceLastDelta`
6. **`done`** → mark `done: true`, reset `hadToolSinceLastDelta`
7. **`user_message`** → always creates a new user bubble; finalizes any open agent message

### Paragraph separators between tool calls

In a multi-turn agent loop, the agent emits text before calling a tool, the tool runs, then the agent emits more text. All of this accumulates into a single `content` string. Without separators, the text runs together as one giant paragraph — markdown rendering cannot fix this because there are no newline characters to parse.

**The fix:** track whether a tool event occurred since the last text delta. If so, insert `\n\n` before the next delta text:

```js
// Module-level state (not per-message — it tracks the live event stream)
let hadToolSinceLastDelta = false;

// In the delta handler:
case 'delta': {
  const text = data.text ?? '';
  const needsSep = hadToolSinceLastDelta;
  hadToolSinceLastDelta = false;
  updateLastAgentMessage(m => {
    const sep = needsSep && m.content && !m.content.endsWith('\n') ? '\n\n' : '';
    return { ...m, content: m.content + sep + text };
  });
  break;
}

// In the tool_start handler:
case 'tool_start': {
  hadToolSinceLastDelta = true;
  // ... rest of handler
}

// Reset on result/done:
case 'result':
case 'done': {
  hadToolSinceLastDelta = false;
  // ... rest of handler
}
```

The `endsWith('\n')` guard prevents double-spacing when the agent's text already ends with a newline.

**Both paths need this.** The live `applySessionEvent()` path uses a module-level flag. The replay `rebuildChatFromEvents()` path uses a local `hadTool` variable with the same logic. Test that both paths produce identical output for the same event sequence.

### Key rule: "ensure current agent message"

```js
function ensureCurrentAgentMessage() {
  const last = messages[messages.length - 1];
  // Reuse existing incomplete agent message
  if (last && last.role === 'agent' && !last.done) return last;
  // Otherwise create a new one
  return createNewAgentMessage();
}
```

The `done` flag is the gate. Once `done: true`, the next event creates a fresh bubble. This is why event ordering matters — if a `done` event gets stored between two `delta` events, replay splits them into two bubbles.

### Rendering: always parse markdown, even during streaming

A common mistake is rendering raw text during streaming and only switching to markdown when the message is done:

```svelte
<!-- BAD: raw text during streaming, markdown only when done -->
{#if msg.done}
  <MarkdownRenderer content={msg.content} />
{:else}
  <div class="raw-text">{msg.content}</div>
{/if}
```

This causes the user to see a "flash" of unformatted text (raw backticks, bare URLs, no paragraph breaks) that suddenly snaps to formatted markdown when the turn completes. Always render through the markdown pipeline:

```svelte
<!-- GOOD: consistent markdown rendering in all states -->
<MarkdownRenderer content={msg.content} />
```

Modern markdown parsers (e.g. `marked`) are fast enough to re-parse on every token delta (~50/sec). Use `white-space: pre-wrap` on the raw text fallback only if you measure a real performance problem with large documents.

### Replay vs live streaming

Events can arrive via two paths:
1. **Live SSE** — events arrive in real time and are applied incrementally via `applySessionEvent()`
2. **Replay on page load** — all stored events are fetched from the API and rebuilt into messages via `rebuildChatFromEvents()`

Both paths must follow the same accumulation logic. The replay path is more sensitive to ordering because it processes all events synchronously — there's no time-based grouping like with live events.

### Event persistence: timestamps + sequence numbers

Event replay correctness requires two things:

1. **Millisecond-precision timestamps** — Extract from the event's `ts` field, not `datetime('now')`. This prevents coarse-grained ordering bugs (split message bubbles).

```go
// BAD: second-precision wall clock
INSERT INTO events (..., created_at) VALUES (..., datetime('now'))

// GOOD: extract millisecond-precision timestamp from the event payload
eventTime := time.Now().UTC().Format("2006-01-02 15:04:05.000")  // fallback
if ts, ok := payload["ts"].(string); ok {
    if t, err := time.Parse(time.RFC3339Nano, ts); err == nil {
        eventTime = t.UTC().Format("2006-01-02 15:04:05.000")
    }
}
```

2. **A monotonic sequence number per session** — Timestamps alone are not enough. LLM token streaming produces 5-10 delta events per millisecond. Without a tiebreaker, `ORDER BY created_at, id` falls back to random UUID order and **scrambles the token sequence**. See "Issue: Scrambled/garbled text on historical session replay" above for the full diagnosis and fix.

```sql
-- Schema: always include seq
CREATE TABLE session_events (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    seq INTEGER NOT NULL DEFAULT 0
);

-- Queries: always order by created_at, seq
SELECT * FROM session_events WHERE session_id = ? ORDER BY created_at, seq
```

---

## Chronological chat rendering (block-based model)

The accumulation pattern above uses flat fields (`content`, `toolEvents`) on each message. This works for basic chat, but breaks down when you need **chronological rendering** — showing text, tool calls, permissions, and errors in the exact order they occurred, interleaved within a single agent message.

### ContentBlock discriminated union

Replace flat fields with a `blocks[]` array as the source of truth on each message. Each block has a `kind` discriminator:

```ts
type ContentBlock =
  | { kind: 'text'; text: string }
  | { kind: 'tool'; toolUseId: string; tool: string; input?: any; output?: string; isError?: boolean; status: 'running' | 'done' }
  | { kind: 'permission'; toolName: string; toolInput?: any; allowed?: boolean; resolved: boolean }
  | { kind: 'proof'; src: string; alt?: string }
  | { kind: 'error'; message: string };
```

Rendering iterates `blocks` in order — each block maps to a distinct visual element in the chat. Text blocks render as markdown, tool blocks render as collapsible tool calls, etc. This preserves chronological ordering naturally.

### syncDerivedFields: backward-compatible migration

When migrating from flat fields to blocks, keep the flat fields as **derived/computed** from `blocks[]` via a `syncDerivedFields()` helper. This lets existing consumers (markdown renderer, search, export) keep reading flat fields while new code iterates blocks.

```ts
function syncDerivedFields(msg: ChatMessage): void {
  // Reconstruct flat content from text blocks
  let content = '';
  let hadNonText = false;
  for (const b of msg.blocks) {
    if (b.kind === 'text') {
      if (hadNonText && content && !content.endsWith('\n')) content += '\n\n';
      content += b.text;
      hadNonText = false;
    } else {
      hadNonText = true;
    }
  }
  msg.content = content;

  // Reconstruct flat arrays from typed blocks
  msg.toolEvents = msg.blocks.filter(b => b.kind === 'tool');
  msg.permissionRequest = msg.blocks.find(b => b.kind === 'permission' && !b.resolved) ?? null;
  msg.proof = msg.blocks.find(b => b.kind === 'proof') ?? null;
  msg.error = msg.blocks.find(b => b.kind === 'error')?.message ?? null;
}
```

Key detail: paragraph breaks (`\n\n`) are inserted between text blocks separated by non-text blocks. This replicates the `hadToolSinceLastDelta` behavior from the flat model.

### getToolResultSummary: collapsed tool call display

When tool calls are collapsed (default state), show a one-line summary instead of raw output. Patterns per tool type:

```ts
function getToolResultSummary(block: ToolBlock): string {
  if (block.status !== 'done') return 'Running...';
  if (!block.output) return 'Done';

  const tool = block.tool;
  const input = block.input;
  const output = block.output;

  // File operations: show the path
  if (['Read', 'Write', 'Edit'].includes(tool) && input?.file_path) {
    return input.file_path;
  }
  // Glob: show pattern alongside count
  if (tool === 'Glob') {
    const lines = output.trim().split('\n').filter(Boolean);
    const count = `${lines.length} file${lines.length !== 1 ? 's' : ''}`;
    return input?.pattern ? `${count}  ${input.pattern}` : `${count} matched`;
  }
  // Grep: show pattern alongside count
  if (tool === 'Grep') {
    const lines = output.trim().split('\n').filter(Boolean);
    const count = `${lines.length} match${lines.length !== 1 ? 'es' : ''}`;
    return input?.pattern ? `${count}  "${input.pattern}"` : count;
  }
  // Codex file-read commands: show file path or short command
  if (['cat', 'head', 'tail', 'less', 'find', 'ls', 'tree', 'stat', 'wc', 'rg'].includes(tool)) {
    if (block.file_path) return block.file_path;
    if (block.command && block.command.length < 80) return block.command;
  }
  // Bash: extract task creation or show short output
  if (tool === 'Bash') {
    const tdMatch = output.match(/CREATED (td-[a-f0-9]+)/);
    if (tdMatch) return `CREATED ${tdMatch[1]}`;
  }
  // Short output passthrough
  if (output.length < 80 && !output.includes('\n')) return output.trim();
  return 'Done';
}
```

### expandedToolOutputs keying strategy

When tracking which tool calls are expanded in the UI, key by block position rather than type-specific array position:

```
GOOD:  `${msgId}-block-${blockIndex}`     // position in blocks[]
BAD:   `${msgId}-tool-${toolEventsIndex}`  // position in toolEvents[]
```

Block-index keys remain stable when non-tool blocks (text, permission, error) are added or removed around them. Type-specific-array keys shift when the array is recomputed.

```ts
// In the UI component
let expandedToolOutputs: Record<string, boolean> = $state({});

function toggleTool(msgId: string, blockIndex: number) {
  const key = `${msgId}-block-${blockIndex}`;
  expandedToolOutputs[key] = !expandedToolOutputs[key];
}
```

### Handler deduplication: applyEventBlocksToMessage

Both the live SSE path (`applySessionEvent`) and the history replay path (`rebuildChatFromEvents`) need to convert raw events into blocks. Extract a shared function:

```ts
function applyEventBlocksToMessage(msg: ChatMessage, event: SessionEvent): void {
  const { type, data } = event;

  switch (type) {
    case 'delta': {
      const lastBlock = msg.blocks[msg.blocks.length - 1];
      if (lastBlock?.kind === 'text') {
        lastBlock.text += data.text;
      } else {
        msg.blocks.push({ kind: 'text', text: data.text });
      }
      break;
    }
    case 'tool_start':
      msg.blocks.push({
        kind: 'tool', toolUseId: data.tool_use_id, tool: data.tool,
        input: data.input, status: 'running',
      });
      break;
    case 'tool_result': {
      const toolBlock = msg.blocks.findLast(
        b => b.kind === 'tool' && b.toolUseId === data.tool_use_id
      );
      if (toolBlock) {
        toolBlock.output = data.output;
        toolBlock.isError = data.is_error;
        toolBlock.status = 'done';
      }
      break;
    }
    case 'permission_request':
      msg.blocks.push({
        kind: 'permission', toolName: data.tool_name,
        toolInput: data.tool_input, resolved: false,
      });
      break;
    // ... other event types
  }

  syncDerivedFields(msg);
}
```

Both callers now delegate to this function, eliminating ~200 lines of duplicated logic. The only difference: `applySessionEvent` manages message creation/lookup, while `rebuildChatFromEvents` processes a batch of events sequentially.

### Paragraph-break reconstruction in block model

When `syncDerivedFields` joins text blocks into the flat `content` field, it must insert `\n\n` between text blocks that were separated by non-text blocks — but only if the accumulated content doesn't already end with `\n`:

```ts
if (hadNonText && content && !content.endsWith('\n')) {
  content += '\n\n';
}
```

This replicates the pre-refactor `hadToolSinceLastDelta` flag behavior. Without it, text before and after tool calls runs together as one paragraph in any consumer that reads the flat `content` field.

---

## Rich component rendering

Agent chat doesn't have to be text bubbles. The agent can render interactive components in the chat stream (generative UI), and the UI can render agent-driven components anywhere in the application — sidebars, panels, canvases. This section covers the patterns for both directions.

The core idea: **tool calls and agent state changes are component selection events**. When the agent calls `get_weather`, the UI doesn't show JSON — it shows a `<WeatherCard>`. When the agent enters a "planning" node, a sidebar panel shows the live plan. The chat becomes a timeline of interactive widgets, not just text.

### The three patterns

| Pattern | Direction | Trigger | Example |
|---------|-----------|---------|---------|
| **Tool-mapped components** | Agent → chat | Tool call lifecycle | `get_weather` → `<WeatherCard>` in message stream |
| **State-projected components** | Agent → anywhere | Agent state change | Planning node active → sidebar shows `<PlanEditor>` |
| **Frontend tools** | UI → agent | User interaction | User clicks "Approve" → agent receives approval and continues |

All three compose together. A single agent turn might render a chart in the chat, update a sidebar panel, and pause for user approval — all driven by the same event stream from the normalized event model above.

---

## The component registry

A component registry maps abstract names to concrete UI components. This is the single most important pattern for rich agent chat — it decouples the agent's tool/state vocabulary from the rendering implementation.

### Registry structure

```ts
// component-registry.ts
import type { ComponentType } from 'svelte';  // or React, etc.

type ComponentEntry = {
  component: ComponentType;
  /** Where this component can render */
  surfaces: ('chat' | 'sidebar' | 'panel' | 'overlay' | 'canvas')[];
  /** Show loading skeleton while tool is running? */
  hasLoadingState: boolean;
};

const registry: Record<string, ComponentEntry> = {};

export function registerComponent(name: string, entry: ComponentEntry) {
  registry[name] = entry;
}

export function getComponent(name: string): ComponentEntry | undefined {
  return registry[name];
}

export function listComponents(surface?: string): string[] {
  if (!surface) return Object.keys(registry);
  return Object.entries(registry)
    .filter(([_, e]) => e.surfaces.includes(surface as any))
    .map(([name]) => name);
}
```

### Registration

Register components at app startup. Each component declares which surfaces it supports:

```ts
// Register at app init
import WeatherCard from './components/WeatherCard.svelte';
import PlanEditor from './components/PlanEditor.svelte';
import CodeDiff from './components/CodeDiff.svelte';
import ApprovalDialog from './components/ApprovalDialog.svelte';

registerComponent('weather', {
  component: WeatherCard,
  surfaces: ['chat', 'panel'],
  hasLoadingState: true,
});
registerComponent('plan_editor', {
  component: PlanEditor,
  surfaces: ['sidebar', 'panel'],
  hasLoadingState: false,
});
registerComponent('code_diff', {
  component: CodeDiff,
  surfaces: ['chat', 'panel', 'overlay'],
  hasLoadingState: true,
});
registerComponent('approval', {
  component: ApprovalDialog,
  surfaces: ['chat'],
  hasLoadingState: false,
});
```

### Why a registry instead of inline switch/case

Switch/case on tool names is the simplest approach and works for small apps:

```ts
// Simple but doesn't scale
switch (toolName) {
  case 'get_weather': return <WeatherCard data={toolResult} />;
  case 'search': return <SearchResults data={toolResult} />;
  default: return <JsonViewer data={toolResult} />;
}
```

The registry is better when:
- Components render in **multiple surfaces** (chat AND sidebar)
- You need **loading states** during tool execution (not just after)
- Components are **added dynamically** (plugins, user customization)
- The agent emits **component events** that don't map 1:1 to tool names

Use switch/case for ≤5 tool-mapped components. Use a registry beyond that.

---

## Agent → chat: tool-mapped components

The most common pattern. When the agent calls a tool, the UI renders a component instead of (or alongside) raw tool output.

### Extending the ContentBlock model

Add a `component` kind to the existing block-based message model:

```ts
type ContentBlock =
  | { kind: 'text'; text: string }
  | { kind: 'tool'; toolUseId: string; tool: string; input?: any; output?: string; isError?: boolean; status: 'running' | 'done' }
  | { kind: 'permission'; toolName: string; toolInput?: any; allowed?: boolean; resolved: boolean }
  | { kind: 'proof'; src: string; alt?: string }
  | { kind: 'error'; message: string }
  // NEW: rich component blocks
  | { kind: 'component'; name: string; props: Record<string, any>; surface: string; status: 'loading' | 'ready' | 'error'; toolUseId?: string };
```

Component blocks can be **standalone** (emitted directly by the agent via custom events) or **tool-linked** (associated with a tool call via `toolUseId`). Tool-linked components replace the default collapsed tool output display.

### Event flow: tool call → component rendering

```
Agent calls get_weather(city: "NYC")
  ↓
tool_start event: { tool: "get_weather", tool_use_id: "tu_123", input: { city: "NYC" } }
  ↓
Registry lookup: getComponent("get_weather") → WeatherCard
  ↓
Push component block: { kind: 'component', name: 'weather', props: { city: "NYC" }, status: 'loading', toolUseId: "tu_123" }
  ↓
tool_result event: { tool_use_id: "tu_123", output: '{"temp": 72, ...}' }
  ↓
Update component block: status → 'ready', merge parsed output into props
```

### Handler integration

Extend `applyEventBlocksToMessage` to create component blocks when a tool has a registered component:

```ts
case 'tool_start': {
  const entry = getComponent(data.tool);
  if (entry && entry.surfaces.includes('chat')) {
    // Render as rich component
    msg.blocks.push({
      kind: 'component',
      name: data.tool,
      props: data.input ?? {},
      surface: 'chat',
      status: entry.hasLoadingState ? 'loading' : 'ready',
      toolUseId: data.tool_use_id,
    });
  }
  // Always push the tool block too (for debugging, expand/collapse)
  msg.blocks.push({
    kind: 'tool', toolUseId: data.tool_use_id, tool: data.tool,
    input: data.input, status: 'running',
  });
  break;
}

case 'tool_result': {
  // Update tool block
  const toolBlock = msg.blocks.findLast(
    b => b.kind === 'tool' && b.toolUseId === data.tool_use_id
  );
  if (toolBlock) {
    toolBlock.output = data.output;
    toolBlock.isError = data.is_error;
    toolBlock.status = 'done';
  }
  // Update component block with result data
  const compBlock = msg.blocks.findLast(
    b => b.kind === 'component' && b.toolUseId === data.tool_use_id
  );
  if (compBlock) {
    try {
      const parsed = JSON.parse(data.output);
      compBlock.props = { ...compBlock.props, ...parsed };
      compBlock.status = data.is_error ? 'error' : 'ready';
    } catch {
      compBlock.status = data.is_error ? 'error' : 'ready';
    }
  }
  break;
}
```

### Rendering in Svelte 5

```svelte
<!-- ChatMessage.svelte -->
<script lang="ts">
  import { getComponent } from './component-registry';

  let { message } = $props();
</script>

{#each message.blocks as block, i}
  {#if block.kind === 'text'}
    <MarkdownRenderer content={block.text} />

  {:else if block.kind === 'component'}
    {@const entry = getComponent(block.name)}
    {#if entry}
      {#if block.status === 'loading' && entry.hasLoadingState}
        <div class="animate-pulse rounded-lg bg-muted h-24 w-full" />
      {:else}
        <entry.component {...block.props} status={block.status} />
      {/if}
    {:else}
      <!-- Fallback: render as collapsed tool output -->
      <ToolCallCollapsed block={block} />
    {/if}

  {:else if block.kind === 'tool'}
    <!-- Only show tool block if no component block covers this toolUseId -->
    {#if !message.blocks.some(b => b.kind === 'component' && b.toolUseId === block.toolUseId)}
      <ToolCallBlock {block} {i} msgId={message.id} />
    {/if}

  {:else if block.kind === 'permission'}
    <PermissionRequest {block} />

  {:else if block.kind === 'error'}
    <ErrorBlock message={block.message} />
  {/if}
{/each}
```

### Component contract

Every component in the registry receives these standard props:

```ts
type ComponentProps = {
  /** Tool input and/or parsed tool output, merged */
  [key: string]: any;
  /** 'loading' while tool is running, 'ready' when result arrives, 'error' on failure */
  status: 'loading' | 'ready' | 'error';
};
```

Components should handle all three states. A weather card might show a skeleton on `loading`, data on `ready`, and an error message on `error`.

---

## Agent → anywhere: state-projected components

Tool-mapped components render in the chat timeline. State-projected components render **anywhere in the application** — they react to agent state changes regardless of which message triggered them.

### The component event

Extend the normalized event model with a new event type for component rendering outside the chat:

```ts
// Add to EventTypes
COMPONENT_UPDATE: 'component_update',
COMPONENT_REMOVE: 'component_remove',
```

```ts
// component_update event
{
  type: 'component_update',
  data: {
    component_id: string,    // Stable ID for this component instance
    name: string,            // Registry name (e.g., 'plan_editor')
    surface: string,         // Target: 'sidebar' | 'panel' | 'overlay' | 'canvas'
    props: Record<string, any>,
    merge: boolean,          // true = merge props into existing, false = replace
  },
  ts: string,
}

// component_remove event
{
  type: 'component_remove',
  data: {
    component_id: string,
  },
  ts: string,
}
```

### Emitting component events from the backend

The backend adapter emits these events when the agent's state warrants a UI update. This can happen:

1. **From tool results** — after a tool completes, the adapter checks if the tool has a surface component and emits a `component_update`
2. **From agent state** — the adapter watches the agent's state (e.g., LangGraph node transitions) and emits updates when relevant state changes
3. **Explicitly** — the agent's tools can emit component events directly via a `render_component` helper

```python
# Python backend: emit component events

def emit_component(session, component_id: str, name: str, surface: str, props: dict, merge: bool = False):
    """Emit a component_update event to the frontend."""
    session.emit({
        "type": "component_update",
        "data": {
            "component_id": component_id,
            "name": name,
            "surface": surface,
            "props": props,
            "merge": merge,
        },
        "ts": datetime.utcnow().isoformat() + "Z",
    })

# Usage in a LangGraph node:
async def planning_node(state: AgentState, config: dict):
    plan = await generate_plan(state)
    session = config["session"]

    # Push plan editor to sidebar
    emit_component(session, "plan-editor", "plan_editor", "sidebar", {
        "steps": plan.steps,
        "current_step": 0,
        "editable": True,
    })

    return {"plan": plan}
```

### Surface manager (frontend)

The surface manager tracks active components across all surfaces and routes updates:

```ts
// surface-manager.ts
import { getComponent } from './component-registry';

type ActiveComponent = {
  id: string;
  name: string;
  surface: string;
  props: Record<string, any>;
};

// Svelte 5: reactive state
let activeComponents: ActiveComponent[] = $state([]);

export function handleComponentEvent(event: SessionEvent) {
  if (event.type === 'component_update') {
    const { component_id, name, surface, props, merge } = event.data;
    const entry = getComponent(name);
    if (!entry || !entry.surfaces.includes(surface)) return;

    const existing = activeComponents.find(c => c.id === component_id);
    if (existing) {
      existing.props = merge ? { ...existing.props, ...props } : props;
      existing.surface = surface;
    } else {
      activeComponents.push({ id: component_id, name, surface, props });
    }
  }

  if (event.type === 'component_remove') {
    activeComponents = activeComponents.filter(c => c.id !== event.data.component_id);
  }
}

export function getComponentsForSurface(surface: string): ActiveComponent[] {
  return activeComponents.filter(c => c.surface === surface);
}

export function clearAllComponents() {
  activeComponents = [];
}
```

### Rendering surface slots in the layout

Place surface slots in your SvelteKit layout. Each slot renders whatever components the agent has pushed to that surface:

```svelte
<!-- +layout.svelte -->
<script lang="ts">
  import { getComponentsForSurface } from './surface-manager';
  import { getComponent } from './component-registry';
  import SurfaceSlot from './SurfaceSlot.svelte';
</script>

<div class="app-layout">
  <aside class="sidebar">
    <SurfaceSlot surface="sidebar" />
  </aside>

  <main>
    <slot />  <!-- Chat lives here -->
  </main>

  <aside class="panel">
    <SurfaceSlot surface="panel" />
  </aside>
</div>

{#if getComponentsForSurface('overlay').length > 0}
  <div class="overlay-container">
    <SurfaceSlot surface="overlay" />
  </div>
{/if}
```

```svelte
<!-- SurfaceSlot.svelte -->
<script lang="ts">
  import { getComponentsForSurface } from './surface-manager';
  import { getComponent } from './component-registry';

  let { surface } = $props();
  let components = $derived(getComponentsForSurface(surface));
</script>

{#each components as active (active.id)}
  {@const entry = getComponent(active.name)}
  {#if entry}
    <entry.component {...active.props} componentId={active.id} />
  {/if}
{/each}
```

### Wiring into the event stream

Add `component_update` and `component_remove` handling to the existing SSE event processor:

```ts
// In your SSE event handler (alongside applySessionEvent)
function handleSessionEvent(event: SessionEvent) {
  if (event.type === 'component_update' || event.type === 'component_remove') {
    handleComponentEvent(event);
    return; // These don't accumulate into chat messages
  }
  // ... existing event handling (delta, tool_start, etc.)
  applySessionEvent(event);
}
```

---

## UI → agent: frontend tools and bidirectional state

The patterns above are agent-to-UI (the agent pushes components). The reverse direction — UI-to-agent — enables truly interactive experiences where user actions in rendered components feed back into the agent's reasoning.

### Pattern 1: Frontend tools (agent calls the UI)

The agent defines a tool that executes on the frontend, not the backend. The agent calls the tool, the frontend renders UI for the user to interact with, and the user's response becomes the tool result.

```ts
// Frontend tool registration
type FrontendTool = {
  name: string;
  description: string;
  parameters: Record<string, any>;  // JSON Schema
  /** Render UI and return the result when the user completes interaction */
  execute: (params: any) => Promise<any>;
};

const frontendTools: Map<string, FrontendTool> = new Map();

export function registerFrontendTool(tool: FrontendTool) {
  frontendTools.set(tool.name, tool);
}

// Example: approval tool
registerFrontendTool({
  name: 'request_approval',
  description: 'Request user approval for a proposed action',
  parameters: {
    type: 'object',
    properties: {
      action: { type: 'string' },
      details: { type: 'string' },
      options: { type: 'array', items: { type: 'string' } },
    },
  },
  execute: async (params) => {
    // Returns a promise that resolves when the user clicks a button
    return new Promise((resolve) => {
      showApprovalDialog({
        ...params,
        onChoice: (choice: string) => resolve({ approved: choice === 'approve', choice }),
      });
    });
  },
});
```

### Intercepting tool calls for frontend execution

When the agent calls a tool that's registered as a frontend tool, intercept it before sending to the backend:

```ts
// In the tool permission/execution layer
async function handleToolCall(toolName: string, toolInput: any, toolUseId: string): Promise<string> {
  const frontendTool = frontendTools.get(toolName);
  if (frontendTool) {
    // Execute on the frontend — this renders UI and waits for user interaction
    const result = await frontendTool.execute(toolInput);
    // Send the result back to the agent as a tool_result
    await session.sendToolResult(toolUseId, JSON.stringify(result));
    return JSON.stringify(result);
  }
  // Not a frontend tool — let the backend handle it
  return null;
}
```

### Pattern 2: Component callbacks (UI pushes state to agent)

Components rendered by the agent can send state back via a callback channel. This is simpler than frontend tools — no tool call/result lifecycle, just a message from the UI to the agent.

```ts
// Callback channel
type ComponentCallback = {
  componentId: string;
  action: string;
  payload: Record<string, any>;
};

export async function sendComponentCallback(callback: ComponentCallback) {
  // Send as the next user message with metadata
  await session.sendMessage(JSON.stringify({
    type: 'component_callback',
    ...callback,
  }));
}
```

```svelte
<!-- PlanEditor.svelte — rendered in sidebar by the agent -->
<script lang="ts">
  import { sendComponentCallback } from './surface-manager';

  let { steps, current_step, editable, componentId } = $props();

  function reorderStep(from: number, to: number) {
    // Optimistic UI update
    const reordered = [...steps];
    const [moved] = reordered.splice(from, 1);
    reordered.splice(to, 0, moved);
    steps = reordered;

    // Notify agent
    sendComponentCallback({
      componentId,
      action: 'reorder_steps',
      payload: { steps: reordered },
    });
  }

  function approveStep(index: number) {
    sendComponentCallback({
      componentId,
      action: 'approve_step',
      payload: { step_index: index },
    });
  }
</script>

<div class="plan-editor">
  {#each steps as step, i}
    <div class="plan-step" class:active={i === current_step}>
      <span>{step.description}</span>
      {#if editable}
        <button onclick={() => approveStep(i)}>Approve</button>
      {/if}
    </div>
  {/each}
</div>
```

### Pattern 3: Shared reactive state (bidirectional sync)

For deep integration, maintain a shared state object that both the agent and UI can read and write. State changes in either direction propagate via events.

```ts
// shared-state.ts
type SharedState = Record<string, any>;

let sharedState: SharedState = $state({});

/** Agent updated state (via SSE event) */
export function applyStateSnapshot(state: SharedState) {
  sharedState = state;
}

/** Agent sent a partial update (via SSE event) */
export function applyStateDelta(patches: JsonPatch[]) {
  // Apply RFC 6902 JSON Patch operations
  for (const patch of patches) {
    switch (patch.op) {
      case 'add':
      case 'replace':
        setNestedValue(sharedState, patch.path, patch.value);
        break;
      case 'remove':
        deleteNestedValue(sharedState, patch.path);
        break;
    }
  }
}

/** UI changed state (sends to agent via POST) */
export async function updateSharedState(path: string, value: any) {
  setNestedValue(sharedState, path, value);  // Optimistic
  await fetch(`/api/sessions/${sessionId}/state`, {
    method: 'PATCH',
    body: JSON.stringify([{ op: 'replace', path, value }]),
  });
}

export function getSharedState(): SharedState {
  return sharedState;
}
```

This is the pattern used by CopilotKit's `useCoAgent` (shared state between frontend and LangGraph agent) and AG-UI's state synchronization protocol. Use it when the agent and UI are co-editing the same data structure (e.g., a document, a plan, a configuration).

---

## Python backend: emitting rich UI events

The frontend patterns above consume events. Here's how to emit them from Python backends.

### Pydantic models for component events

```python
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Any, Literal
import json

class ComponentUpdate(BaseModel):
    type: Literal["component_update"] = "component_update"
    data: "ComponentUpdateData"
    ts: str

    @classmethod
    def create(cls, component_id: str, name: str, surface: str, props: dict, merge: bool = False):
        return cls(
            data=ComponentUpdateData(
                component_id=component_id,
                name=name,
                surface=surface,
                props=props,
                merge=merge,
            ),
            ts=datetime.now(timezone.utc).isoformat(),
        )

class ComponentUpdateData(BaseModel):
    component_id: str
    name: str
    surface: str
    props: dict[str, Any]
    merge: bool = False

class ComponentRemove(BaseModel):
    type: Literal["component_remove"] = "component_remove"
    data: "ComponentRemoveData"
    ts: str

    @classmethod
    def create(cls, component_id: str):
        return cls(
            data=ComponentRemoveData(component_id=component_id),
            ts=datetime.now(timezone.utc).isoformat(),
        )

class ComponentRemoveData(BaseModel):
    component_id: str
```

### SSE emission from FastAPI / Starlette

```python
from starlette.responses import StreamingResponse
import asyncio

class SessionEventEmitter:
    """Manages an SSE stream for a session, including component events."""

    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()

    async def emit(self, event: dict):
        await self._queue.put(event)

    async def emit_component(self, component_id: str, name: str, surface: str, props: dict, merge: bool = False):
        await self.emit(
            ComponentUpdate.create(component_id, name, surface, props, merge).model_dump()
        )

    async def remove_component(self, component_id: str):
        await self.emit(
            ComponentRemove.create(component_id).model_dump()
        )

    async def stream(self):
        while True:
            event = await self._queue.get()
            yield f"data: {json.dumps(event)}\n\n"
```

### Integration with LangGraph

In a LangGraph agent, emit component events from node functions:

```python
from langgraph.graph import StateGraph

async def research_node(state: dict, config: dict):
    emitter: SessionEventEmitter = config["configurable"]["emitter"]

    # Push a progress component to the sidebar
    await emitter.emit_component(
        component_id="research-progress",
        name="research_progress",
        surface="sidebar",
        props={"queries": [], "results_count": 0, "status": "starting"},
    )

    for i, query in enumerate(state["queries"]):
        results = await search(query)
        state["results"].extend(results)

        # Update progress (merge mode — only send changed props)
        await emitter.emit_component(
            component_id="research-progress",
            name="research_progress",
            surface="sidebar",
            props={
                "queries": state["queries"][:i+1],
                "results_count": len(state["results"]),
                "status": "searching",
            },
            merge=True,
        )

    # Final update
    await emitter.emit_component(
        component_id="research-progress",
        name="research_progress",
        surface="sidebar",
        props={"status": "complete"},
        merge=True,
    )

    return state
```

### Integration with plain Claude SDK / tool wrappers

For simpler setups without LangGraph, emit component events from tool result handlers:

```python
# In the adapter layer that wraps Claude SDK
async def on_tool_result(session, tool_name: str, tool_use_id: str, result: str):
    """Called after a tool completes. Emits component events if the tool has a UI mapping."""

    TOOL_COMPONENT_MAP = {
        "get_weather": ("weather", "chat"),
        "generate_chart": ("chart", "chat"),
        "update_plan": ("plan_editor", "sidebar"),
        "search_docs": ("search_results", "panel"),
    }

    if tool_name in TOOL_COMPONENT_MAP:
        name, surface = TOOL_COMPONENT_MAP[tool_name]
        try:
            props = json.loads(result)
        except json.JSONDecodeError:
            props = {"raw": result}

        await session.emitter.emit_component(
            component_id=f"{tool_name}-{tool_use_id}",
            name=name,
            surface=surface,
            props=props,
        )
```

---

## Human-in-the-loop: renderAndWait

A common pattern where the agent pauses, the UI renders an interactive component, and the agent resumes when the user completes an action. This combines frontend tools with component rendering.

### The interrupt event

```ts
// Add to EventTypes
INTERRUPT: 'interrupt',
INTERRUPT_RESOLVED: 'interrupt_resolved',
```

```ts
// interrupt event
{
  type: 'interrupt',
  data: {
    interrupt_id: string,
    component_name: string,     // Registry name for the interrupt UI
    props: Record<string, any>, // Data to display
    surface: string,            // Where to render ('chat' | 'overlay')
  },
  ts: string,
}
```

### Frontend handling

```ts
let pendingInterrupt: { id: string; resolve: (value: any) => void } | null = null;

function handleInterruptEvent(event: SessionEvent) {
  if (event.type !== 'interrupt') return;
  const { interrupt_id, component_name, props, surface } = event.data;

  // Push to appropriate surface with a resolve callback
  const entry = getComponent(component_name);
  if (!entry) return;

  if (surface === 'chat') {
    // Add as a component block in the current message
    currentMessage.blocks.push({
      kind: 'component',
      name: component_name,
      props: {
        ...props,
        onResolve: async (value: any) => {
          await resolveInterrupt(interrupt_id, value);
        },
      },
      surface: 'chat',
      status: 'ready',
    });
  } else {
    // Push to surface manager with resolve callback
    handleComponentEvent({
      type: 'component_update',
      data: {
        component_id: `interrupt-${interrupt_id}`,
        name: component_name,
        surface,
        props: {
          ...props,
          onResolve: async (value: any) => {
            await resolveInterrupt(interrupt_id, value);
            handleComponentEvent({
              type: 'component_remove',
              data: { component_id: `interrupt-${interrupt_id}` },
              ts: new Date().toISOString(),
            });
          },
        },
        merge: false,
      },
      ts: event.ts,
    });
  }
}

async function resolveInterrupt(interruptId: string, value: any) {
  await fetch(`/api/sessions/${sessionId}/interrupt/${interruptId}`, {
    method: 'POST',
    body: JSON.stringify({ value }),
  });
}
```

### Python backend: pausing for interrupt

```python
async def approval_node(state: dict, config: dict):
    emitter: SessionEventEmitter = config["configurable"]["emitter"]
    interrupt_id = str(uuid4())

    # Emit interrupt — agent pauses here
    await emitter.emit({
        "type": "interrupt",
        "data": {
            "interrupt_id": interrupt_id,
            "component_name": "approval",
            "props": {
                "action": state["proposed_action"],
                "details": state["action_details"],
                "options": ["approve", "reject", "modify"],
            },
            "surface": "chat",
        },
        "ts": datetime.now(timezone.utc).isoformat(),
    })

    # Wait for resolution
    resolution = await wait_for_interrupt_resolution(interrupt_id)
    state["approval"] = resolution
    return state
```

---

## Streaming component updates (progressive rendering)

Some components need to update progressively as data streams in — a chart that builds bar by bar, a document that types out, a map that adds pins. Use merge-mode component updates for this.

### Pattern: streaming props via merge

```python
# Backend: stream chart data points
async def generate_chart_node(state: dict, config: dict):
    emitter = config["configurable"]["emitter"]
    component_id = "live-chart"

    # Initial empty chart
    await emitter.emit_component(component_id, "chart", "chat", {
        "type": "bar",
        "data": [],
        "title": "Sales by Region",
    })

    for region in state["regions"]:
        sales = await fetch_sales(region)

        # Merge new data point
        await emitter.emit_component(component_id, "chart", "chat", {
            "data": [...existing_data, {"region": region, "sales": sales}],
        }, merge=True)

    await emitter.emit_component(component_id, "chart", "chat", {
        "status": "complete",
    }, merge=True)
```

### Frontend: handling merge updates

The surface manager's `handleComponentEvent` already handles merge. For chat-inline components, the same merge logic applies to the component block's props:

```ts
case 'component_update': {
  const { component_id, props, merge } = event.data;

  // Find existing component block in messages
  for (const msg of messages) {
    const block = msg.blocks.find(
      b => b.kind === 'component' && b.componentId === component_id
    );
    if (block) {
      block.props = merge ? { ...block.props, ...props } : props;
      break;
    }
  }
  break;
}
```

For deep merges (nested objects, array appends), use a proper deep merge or JSON Patch instead of shallow spread. Shallow merge is fine for most cases — use deep merge only when components have nested state.

---

## Reference: existing libraries

When building rich agent chat, consider these libraries before building from scratch. Each excels at a different point in the design space.

### When to use Vercel AI SDK

Best for: **Next.js apps** with tool-calling agents where you want typed tool-to-component mapping.

- `useChat` with typed message `parts` gives you `tool-{name}` discriminated unions
- Tool part states (`input-streaming` → `input-available` → `output-available`) drive loading/ready/error rendering
- `ToolLoopAgent` (SDK v6) handles multi-step agent loops automatically
- Works well when the chat is the primary UI and components are inline

Limitation: React + Next.js only for the RSC path. The `useChat` approach is more portable.

### When to use CopilotKit

Best for: **Deep agent-UI integration** where the agent and UI share state bidirectionally.

- `useCoAgent` provides shared reactive state between frontend and LangGraph agent
- `useCoAgentStateRender` renders agent state as components in chat, keyed by LangGraph node name
- `useFrontendTool` / `renderAndWait` handles human-in-the-loop with component rendering
- AG-UI protocol provides a standard event layer (state snapshots, deltas, tool lifecycles)

Limitation: React-only. Tightly coupled to LangGraph on the backend.

### When to use LangGraph agent-chat-ui

Best for: **LangGraph-native apps** that need server-defined components with shadow DOM isolation.

- Server registers UI components in `langgraph.json` → bundled and served to the client
- `LoadExternalComponent` renders in shadow DOM for style isolation
- `UIMessage` custom events with merge support for progressive rendering
- Artifact system (portal-based side panel) for rendering outside the chat

Limitation: React + Next.js. Requires LangSmith for component bundling in production.

### When to build custom (this skill's patterns)

Build custom when:

- You're using **SvelteKit or another non-React framework**
- Your backend is **Python without LangGraph** (plain Claude SDK, custom agents)
- You need **multiple surface targets** (sidebar + panel + overlay) driven by the same agent
- You want **framework-agnostic patterns** that aren't locked to a specific agent runtime
- You're already using the adapter layer from this skill and want to extend it

The patterns in this section are designed to compose with the event normalization and chat rendering patterns above. They work with any backend that can emit SSE events.

---

## Checklist: adding rich components to an existing chat

1. **Define the component** — Svelte component that accepts props + `status`
2. **Register it** — add to component registry with surface list
3. **Map the trigger** — tool name in `TOOL_COMPONENT_MAP` (backend) or registry lookup on `tool_start` (frontend)
4. **Emit events** — `component_update` from backend for surface-targeted components
5. **Handle in event stream** — extend `handleSessionEvent` to route component events
6. **Render** — component blocks in chat, `SurfaceSlot` for other surfaces
7. **Wire callbacks** — `sendComponentCallback` or frontend tools for UI→agent communication
8. **Test replay** — component blocks must reconstruct correctly from persisted events
