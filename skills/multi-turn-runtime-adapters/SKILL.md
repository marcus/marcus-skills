---
name: multi-turn-runtime-adapters
description: Adapt AI agent runtimes (Claude Code SDK, Codex CLI app-server) into multi-turn conversational systems. Covers session lifecycle, resume/fork, event normalization, JSON-RPC 2.0 over stdio, and tool policy enforcement. Use when building orchestrators, chat UIs, or sidecar processes that need persistent multi-turn agent sessions.
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

Do **not** use this skill for:

- One-shot agent invocations (just use `query()` or `codex exec` directly)
- Building the agent runtimes themselves
- Frontend/UI implementation (this covers the backend adapter layer)

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
    parent_tool_use_id: null,
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
| `item/agentMessage/delta` | `delta` | Streaming text chunks |
| `item/completed` (agentMessage) | **SKIP** | Text already delivered via streaming deltas — emitting here causes duplicates |
| `item/reasoning/textDelta` | `thinking` | Streaming reasoning |
| `item/reasoning/summaryTextDelta` | `thinking` | |
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
