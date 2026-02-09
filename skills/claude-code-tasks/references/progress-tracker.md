# Real-Time Progress Tracker

Full-featured classes for tracking todo changes with change detection, progress bars, and completion callbacks.

## TypeScript: TodoTracker Class

```typescript
import { query, type SDKMessage } from "@anthropic-ai/claude-agent-sdk";

interface Todo {
  content: string;
  status: "pending" | "in_progress" | "completed";
  activeForm: string;
}

type TodoChangeCallback = (todos: Todo[], changes: TodoChange[]) => void;

interface TodoChange {
  type: "added" | "removed" | "status_changed";
  todo: Todo;
  previousStatus?: string;
}

class TodoTracker {
  private todos: Todo[] = [];
  private listeners: TodoChangeCallback[] = [];

  onChange(callback: TodoChangeCallback) {
    this.listeners.push(callback);
  }

  update(newTodos: Todo[]) {
    const changes = this.detectChanges(newTodos);
    this.todos = newTodos;
    if (changes.length > 0) {
      this.listeners.forEach(cb => cb(this.todos, changes));
    }
  }

  get progress() {
    const total = this.todos.length;
    const completed = this.todos.filter(t => t.status === "completed").length;
    const inProgress = this.todos.filter(t => t.status === "in_progress").length;
    return { total, completed, inProgress, pending: total - completed - inProgress };
  }

  get progressBar() {
    const { total, completed } = this.progress;
    if (total === 0) return "";
    const pct = Math.round((completed / total) * 100);
    const filled = Math.round(pct / 5);
    return `[${"#".repeat(filled)}${".".repeat(20 - filled)}] ${pct}% (${completed}/${total})`;
  }

  private detectChanges(newTodos: Todo[]): TodoChange[] {
    const changes: TodoChange[] = [];
    const oldMap = new Map(this.todos.map(t => [t.content, t]));
    const newMap = new Map(newTodos.map(t => [t.content, t]));

    for (const [content, todo] of newMap) {
      const old = oldMap.get(content);
      if (!old) {
        changes.push({ type: "added", todo });
      } else if (old.status !== todo.status) {
        changes.push({ type: "status_changed", todo, previousStatus: old.status });
      }
    }
    for (const [content, todo] of oldMap) {
      if (!newMap.has(content)) {
        changes.push({ type: "removed", todo });
      }
    }
    return changes;
  }
}

// Usage
const tracker = new TodoTracker();

tracker.onChange((todos, changes) => {
  console.clear();
  console.log(tracker.progressBar);
  console.log();
  for (const todo of todos) {
    const icon = todo.status === "completed" ? "done" :
                 todo.status === "in_progress" ? ">>" : "  ";
    const text = todo.status === "in_progress" ? todo.activeForm : todo.content;
    console.log(`  [${icon}] ${text}`);
  }
  console.log();
  for (const change of changes) {
    if (change.type === "status_changed") {
      console.log(`  * ${change.todo.content}: ${change.previousStatus} -> ${change.todo.status}`);
    }
  }
});

for await (const message of query({
  prompt: "Build a complete auth system with todos",
  options: { maxTurns: 20 }
})) {
  if (message.type === "assistant") {
    for (const block of message.message.content) {
      if (block.type === "tool_use" && block.name === "TodoWrite") {
        tracker.update(block.input.todos);
      }
    }
  }
}
```

## Python: TodoTracker Class

```python
from claude_agent_sdk import query, AssistantMessage, ToolUseBlock
from dataclasses import dataclass
from typing import Callable

@dataclass
class TodoChange:
    type: str  # "added", "removed", "status_changed"
    content: str
    status: str
    previous_status: str | None = None

class TodoTracker:
    def __init__(self):
        self.todos: list[dict] = []
        self._listeners: list[Callable] = []

    def on_change(self, callback: Callable):
        self._listeners.append(callback)

    def update(self, new_todos: list[dict]):
        changes = self._detect_changes(new_todos)
        self.todos = new_todos
        if changes:
            for cb in self._listeners:
                cb(self.todos, changes)

    @property
    def progress(self):
        total = len(self.todos)
        completed = sum(1 for t in self.todos if t["status"] == "completed")
        in_progress = sum(1 for t in self.todos if t["status"] == "in_progress")
        return {"total": total, "completed": completed, "in_progress": in_progress, "pending": total - completed - in_progress}

    def _detect_changes(self, new_todos):
        changes = []
        old_map = {t["content"]: t for t in self.todos}
        new_map = {t["content"]: t for t in new_todos}

        for content, todo in new_map.items():
            old = old_map.get(content)
            if not old:
                changes.append(TodoChange("added", content, todo["status"]))
            elif old["status"] != todo["status"]:
                changes.append(TodoChange("status_changed", content, todo["status"], old["status"]))

        for content in old_map:
            if content not in new_map:
                changes.append(TodoChange("removed", content, old_map[content]["status"]))

        return changes

# Usage
tracker = TodoTracker()

def on_update(todos, changes):
    p = tracker.progress
    print(f"\nProgress: {p['completed']}/{p['total']}")
    for todo in todos:
        icon = {"completed": "done", "in_progress": ">>", "pending": "  "}[todo["status"]]
        print(f"  [{icon}] {todo['content']}")
    for c in changes:
        if c.type == "status_changed":
            print(f"  * {c.content}: {c.previous_status} -> {c.status}")

tracker.on_change(on_update)

async for message in query(
    prompt="Build a complete auth system with todos",
    options={"max_turns": 20}
):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, ToolUseBlock) and block.name == "TodoWrite":
                tracker.update(block.input["todos"])
```

## Webhook Integration Example

Push todo updates to an external webhook (e.g., Slack, Discord, a dashboard):

```typescript
tracker.onChange(async (todos, changes) => {
  await fetch("https://your-webhook.example.com/todos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      todos,
      changes: changes.map(c => ({
        type: c.type,
        content: c.todo.content,
        status: c.todo.status
      })),
      progress: tracker.progress,
      timestamp: new Date().toISOString()
    })
  });
});
```
