# Subagent Patterns

Advanced patterns for working with subagents in the Claude Agent SDK.

## Resuming Subagents

Subagents can be resumed to continue where they left off, retaining their full conversation history.

### Pattern: Capture and Resume

```typescript
import { query, type SDKMessage } from "@anthropic-ai/claude-agent-sdk";

// Helper: extract agentId from message content
function extractAgentId(message: SDKMessage): string | undefined {
  if (!("message" in message)) return undefined;
  const content = JSON.stringify(message.message.content);
  const match = content.match(/agentId:\s*([a-f0-9-]+)/);
  return match?.[1];
}

let agentId: string | undefined;
let sessionId: string | undefined;

// First invocation
for await (const message of query({
  prompt: "Use the Explore agent to find all API endpoints",
  options: { allowedTools: ["Read", "Grep", "Glob", "Task"] }
})) {
  if ("session_id" in message) sessionId = message.session_id;
  const id = extractAgentId(message);
  if (id) agentId = id;
}

// Resume later with follow-up
if (agentId && sessionId) {
  for await (const message of query({
    prompt: `Resume agent ${agentId} and list the top 3 most complex endpoints`,
    options: {
      allowedTools: ["Read", "Grep", "Glob", "Task"],
      resume: sessionId  // Must resume same session to access subagent transcript
    }
  })) {
    if ("result" in message) console.log(message.result);
  }
}
```

### Python Version

```python
import re, json, asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

def extract_agent_id(text: str) -> str | None:
    match = re.search(r"agentId:\s*([a-f0-9-]+)", text)
    return match.group(1) if match else None

async def main():
    agent_id = session_id = None

    async for message in query(
        prompt="Use the Explore agent to find all API endpoints",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Grep", "Glob", "Task"])
    ):
        if hasattr(message, "session_id"):
            session_id = message.session_id
        if hasattr(message, "content"):
            extracted = extract_agent_id(json.dumps(message.content, default=str))
            if extracted:
                agent_id = extracted

    if agent_id and session_id:
        async for message in query(
            prompt=f"Resume agent {agent_id} and list the top 3 most complex endpoints",
            options=ClaudeAgentOptions(
                allowed_tools=["Read", "Grep", "Glob", "Task"],
                resume=session_id
            )
        ):
            if hasattr(message, "result"):
                print(message.result)

asyncio.run(main())
```

## AgentDefinition Reference

```typescript
type AgentDefinition = {
  description: string;   // When to delegate to this agent (natural language)
  prompt: string;        // System prompt defining the agent's behavior
  tools?: string[];      // Allowed tools. Omit to inherit all from parent.
  model?: 'sonnet' | 'opus' | 'haiku' | 'inherit';  // Model override
}
```

## Common Tool Combinations

| Use Case | Tools | Notes |
|----------|-------|-------|
| Read-only analysis | `Read`, `Grep`, `Glob` | Can't modify or execute |
| Test execution | `Bash`, `Read`, `Grep` | Can run commands |
| Code modification | `Read`, `Edit`, `Write`, `Grep`, `Glob` | No command execution |
| Full access | (omit `tools`) | Inherits everything |

## Dynamic Agent Factory

Create agents with runtime configuration:

```typescript
function createReviewer(strictness: "basic" | "strict"): AgentDefinition {
  return {
    description: "Code review specialist",
    prompt: `You are a ${strictness === "strict" ? "strict" : "balanced"} code reviewer...`,
    tools: ["Read", "Grep", "Glob"],
    model: strictness === "strict" ? "opus" : "sonnet"
  };
}

// Use at query time
const result = query({
  prompt: "Review the auth module",
  options: {
    allowedTools: ["Read", "Grep", "Glob", "Task"],
    agents: { "reviewer": createReviewer("strict") }
  }
});
```

## Detecting Subagent Messages

Messages from within a subagent's context include `parent_tool_use_id`:

```typescript
for await (const message of query({ prompt: "...", options: { ... } })) {
  // Is this message from inside a subagent?
  if ("parent_tool_use_id" in message && message.parent_tool_use_id) {
    console.log("(from subagent)");
  }

  // Was a subagent just invoked?
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "tool_use" && block.name === "Task") {
        console.log(`Delegated to: ${block.input.subagent_type}`);
        console.log(`Task: ${block.input.description}`);
      }
    }
  }
}
```

## Key Constraints

- Subagents **cannot** spawn their own subagents (no Task tool in subagent tools).
- `Task` must be in the parent's `allowedTools`.
- Subagent transcripts persist in `~/.claude/projects/{project}/{session}/subagents/`.
- Transcripts survive main conversation compaction.
- Default cleanup: 30 days.
