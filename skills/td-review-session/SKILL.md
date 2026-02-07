---
name: td-review-session
description: Start a td review session and do a detailed review of open reviews. Fix obvious bugs immediately, create tasks for bigger issues, ensure test coverage, and use parallel subagents for independent reviews. Use when you want to review and triage pending td reviews.
---

# TD Review Session

You are a review session orchestrator. Start a td review session, review all pending items, fix what you can, and create tasks for everything else. Use subagents for parallel reviews. All state lives in td.

## Session Start

```bash
td usage --new-session
td reviewable
```

Read the output. This gives you every pending review. That is your work queue.

## Classify Reviews

Run `td show <id>` and `td context <id>` for each reviewable item. Classify each into:

| Category | Action |
|----------|--------|
| **Obvious fix** | Create td bug task, fix immediately, approve original review |
| **Needs tests** | Create td task for test coverage |
| **Bigger issue** | Create td task with detailed description for a future session |
| **Clean / Approvable** | Approve |
| **Unclear** | Ask the user a question before proceeding |

## Core Loop

1. **Gather**: Run `td reviewable` to get all pending reviews.
2. **Parallel triage**: For reviews with no dependencies between them, spawn subagents in parallel (one per review) to do the detailed review. Each subagent:
   - Runs `td show <id>` and `td context <id>`
   - Reads all linked files (`td files <id>`) and reviews the actual code changes
   - Classifies the review (see table above)
   - Reports back: classification, summary, and any issues found
3. **Act on results** (sequentially, to avoid conflicts):
   - **Obvious fixes**: Create a bug task (`td create "Fix: <description>" --type bug --priority P1`), implement the fix, commit, then `td approve <original-id>`
   - **Missing tests**: Create a task (`td create "Add tests for <area>" --type task --priority P2`) with a detailed description of what needs testing and why
   - **Bigger issues**: Create a task (`td create "<title>" --type bug --priority <P1|P2>`) with a detailed description including: what's wrong, where it is, suggested fix approach, and any context from the review
   - **Clean**: `td approve <id>`
   - **Unclear**: Ask the user, then act on their answer
4. **Close related tasks**: After fixing bugs related to reviewed items, check for any in-progress tasks that are now resolved. Close them:
   ```bash
   td list --status in_progress
   # For each task that is resolved by the fixes:
   td approve <id>
   ```
5. **Summary**: Report what was reviewed, approved, fixed, and what new tasks were created.

## Subagent Instructions

When spawning review subagents via Task tool, include this in every prompt:

> You are reviewing td task `<id>` in repo `<repo-path>`. Run `td show <id>` and `td context <id>` to understand the task. Run `td files <id>` to see linked files, then read and review the actual code changes thoroughly. Check for:
> - Correctness: Does the code do what the task says?
> - Edge cases: Missing null checks, off-by-ones, unhandled errors
> - Tests: Are there tests? Do they cover the changes?
> - Style: Does it match the surrounding code?
>
> Report back with:
> 1. Classification: obvious-fix | needs-tests | bigger-issue | clean | unclear
> 2. Summary of findings (2-3 sentences)
> 3. If obvious-fix: exact description of the problem and the fix
> 4. If needs-tests: what specifically needs testing
> 5. If bigger-issue: detailed description of the problem, location, and suggested approach
> 6. If unclear: what question to ask the user
>
> Use `td log` to record your findings. Do NOT approve or reject — the orchestrator handles that.

## Rules

- **Fix obvious bugs immediately.** Don't defer what can be fixed in 5 minutes. Create a td bug task first so it's tracked, fix it, then re-submit it for review.
- **Detailed descriptions always.** Every td task you create must have enough context for a future agent to pick it up cold — what's wrong, where, why, and how to fix it.
- **Tests are mandatory.** If a reviewed change lacks tests, create a task for it. Note specifically what needs testing.
- **Parallel when possible.** Independent reviews should be reviewed by subagents in parallel. Only serialize when reviews touch the same files or have dependencies.
- **Close what's done.** After fixing bugs, scan in-progress tasks and close any that are now resolved. Don't leave stale in-progress tasks.
- **Ask, don't guess.** If something is unclear, ask the user. Don't approve or reject unclear code.
- **All state in td.** Log findings with `td log`, decisions with `td log --decision`, blockers with `td log --blocker`. No in-memory state.

## On Compaction / Handoff

Before context runs out:

```bash
td ws handoff
```

Or for a single focus:

```bash
td handoff <current-task-id> \
  --done "reviewed: <ids approved>, fixed: <ids fixed>" \
  --remaining "pending reviews: <ids>, created tasks: <ids>" \
  --decision "key review decisions" \
  --uncertain "items needing user input"
```

Tell the user: "Resume with `/td-review-session` to continue the review."
