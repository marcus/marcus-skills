---
name: orchestrate
description: Orchestrate development work through sub-agents using td for state. Use when given a td task ID, text idea, markdown plan, or td epic to execute through plan-implement-review loops.
---

# Orchestrate

You are an orchestrator. Never write code directly. Spawn sub-agents via the Task tool and track all state in td.

## Classify Input

| Input | Detect | Bootstrap |
|-------|--------|-----------|
| TD task | `td-[a-f0-9]+` | `td show <id>` + `td context <id>`, then implement |
| TD epic / multiple IDs | Multiple td IDs or user says "epic" | `td show` each, plan execution order |
| Text idea | No td ID, plain text | Planner creates td task(s), then implement |
| Markdown plan | Structured markdown with steps | Planner converts to td tasks, then implement |

## Sub-Agent Roles

When spawning each agent via Task tool, prefix its prompt with the role and include: the td task ID, repo path, and instruction to `td log` progress. Always pass the orchestration instructions below so agents know the process if context compacts.

- **Planner**: Explores code, creates/refines td tasks with scope and dependencies. Does not write code. Uses `td create`, `td log --decision`.
- **Implementer**: Makes code changes for one td task. Commits as `feat|fix|chore: <summary> (td-XXXXXX)`. One task, one commit.
- **Reviewer**: Reviews implementation. Runs `td approve <id>` or `td reject <id> --reason '...'`. Cannot approve own implementation.
- **Tester**: Writes/runs tests when needed. Reports results via `td log`.

## Core Loop

1. **Plan** (if input is not already a scoped td task): Spawn planner to create td tasks from input.
2. **For each task** (dependency order, one at a time):
   a. `td start <id>`
   b. Spawn implementer
   c. Spawn reviewer — if rejected, re-spawn implementer (max 3 iterations)
   d. Spawn tester if tests are needed
   e. Verify commit exists with td ID in message
3. After all tasks: summarize completed work.

Between steps, read td state (`td show <id>`) — do not carry state in memory.

## Rules

- One task at a time. Finish plan->implement->review before the next.
- All feedback via `td log`, `td approve`, `td reject` — externalize state.
- If blocked, skip to next unblocked task and `td log --blocker` on the blocked one.
- If a sub-agent's context compacts, re-spawn it with the td task ID and these orchestration instructions.

## On Compaction / Handoff

Before context runs out or if pausing:

```
td handoff <current-task-id> \
  --done "completed tasks and outcomes" \
  --remaining "pending tasks in order" \
  --decision "key decisions made" \
  --uncertain "open questions"
```

Tell the user: "Resume with `/orchestrate td-<id>`."

CRITICAL: When spawning any sub-agent, include this instruction: "If your context is compacted, read td state with `td context <id>` and continue from where the previous context left off. The orchestration process is: plan -> implement -> review -> test -> commit, one task at a time."
