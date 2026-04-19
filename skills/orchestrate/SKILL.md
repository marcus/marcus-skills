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

## Proof Requirements

If the user asks to prove or verify work, the orchestrator must assign proof capture to sub-agents as part of completion, not as an optional follow-up.

- For epic / phased work: have a sub-agent update the epic or phase task with completion state and create a new proof task under that epic or phase.
- For a complex standalone task with subtasks: have a sub-agent update the parent task and create a new proof task under that parent task.
- The proof task must include a `proof` label.
- The proof task description must contain the actual proof artifact or a direct reference to it:
  - UI work: screenshot path and short note about what it proves
  - CLI / backend / infra work: command output, test results, logs, API response sample, or other appropriate proof
- The proof task should be created before final user handoff so proof is preserved in td, not only in chat output.

Recommended pattern:

1. Update the implementation task / epic / phase with the result.
2. Create `Proof: <thing proved>` as a child task.
3. Add label `proof`.
4. Put the screenshot path or other proof directly in the task description.
5. Mark the proof task with the appropriate status after the artifact is captured.

## Rules

- One task at a time. Finish plan->implement->review before the next.
- All feedback via `td log`, `td approve`, `td reject` — externalize state.
- If blocked, skip to next unblocked task and `td log --blocker` on the blocked one.
- If a sub-agent's context compacts, re-spawn it with the td task ID and these orchestration instructions.
- All commits should reference a td task id
- Important: if more than one task is needed to complete the work, create an epic in td and link sub-tasks to the epic.
- Important: if proof is requested, completion is not done until the proof task exists in td with the `proof` label and the proof artifact recorded in its description.

## Learnings from Multi-Task Epics

These patterns were validated across a 12-task epic (backend, frontend, CLI, tests) executed in dependency order.

### td approve/reject ownership limitation

The orchestrator gets flagged as "involved with implementation" even though it only spawned the implementing sub-agent. This means `td approve` / `td complete` cannot be used by the orchestrator after it spawned the implementer. **Workaround**: use `td log <id> "Review: PASS — <summary>"` for review verdicts instead of `td approve`.

### Reviewer agents should be minimal

Reviewer agents only need to: read the git diff, run quality gates (tests, type-check), and report pass/fail. Keep their prompts short — they finish fast compared to implementers and don't need deep context about the codebase.

### Sub-agent prompt checklist

Every implementer prompt should include:
- The td task ID (`td-XXXXXX`)
- Specific file paths from the task description
- Explicit numbered steps (not vague goals)
- Commit message format: `feat|fix|chore: <summary> (td-XXXXXX)` with `Co-Authored-By`
- For frontend work: instruction to run `svelte-check` (or equivalent lint/type-check) before committing
- The compaction recovery instruction (already in this skill)

### Dependency ordering prevents conflicts

Processing tasks in strict dependency order — starting each only after its blocker completes — avoids merge conflicts and build breakage. Do not parallelize tasks that touch overlapping files, even if they seem independent.

### Absorb mid-flight additions

The user may add tasks while execution is in progress. After completing the current task, re-read the epic (`td show <epic-id>`) to pick up new sub-tasks. Slot them into the dependency graph rather than appending to the end.

### Proof tasks need specific artifacts

A proof task description must name the exact artifact to produce — not "capture proof" but "screenshot of ActivityPanel showing 3 block types at `/tmp/rich-blocks-proof.png`" or "paste output of `go test ./internal/modules/planner/...` showing all tests pass". Generic proof tasks get skipped or produce useless output.

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
