---
name: orchestrate
description: Orchestrate development work through sub-agents using td for state. Use when given a td task ID, text idea, markdown plan, or td epic to execute through plan-implement-review loops.
---

# Orchestrate

Guidance for running multi-step development work through sub-agents, with `td` as the durable state store. Use your judgment — this describes a default shape, not a protocol to follow literally.

The one thing worth holding onto: **work gets independently reviewed before it closes.** Most of the rest is negotiable.

## Classify Input

| Input | Detect | Bootstrap |
|-------|--------|-----------|
| td task | `td-[a-f0-9]+` | `td show <id>` + `td context <id>`, then implement |
| td epic / multiple IDs | Multiple td IDs or user says "epic" | `td show` each, plan execution order |
| Text idea | No td ID, plain text | Create td task(s), then implement |
| Markdown plan | Structured markdown with steps | Convert to td tasks, then implement |

If more than one task is needed, create an epic and link the sub-tasks to it.

## Your role

Mostly you delegate: spawn sub-agents via the Task tool, keep state in td, and stay out of the weeds so your context lasts. But you don't have to be a pure router.

- **Planning**: if you already explored the code and know what needs to happen, write the plan and the td tasks yourself. Spawning a planner to rediscover what you already know wastes a context window. Delegate planning when the area is unfamiliar or large.
- **Code**: prefer delegating implementation — it protects your context and creates the separation that makes review meaningful. Small mechanical edits (a typo, a version bump, a one-line fix you already diagnosed) are fine to do directly; just don't then be the only reviewer of them.
- **Review**: don't review work you implemented. That's the line worth keeping.

## Sub-agent roles

Prefix each agent's prompt with its role and include the td task ID, repo path, and an instruction to `td log` progress.

- **Implementer**: makes changes for one or more td tasks. Commits as `feat|fix|chore: <summary> (td-XXXXXX)`.
- **Reviewer**: reads the diff, runs quality gates, records a verdict. Keep reviewer prompts short — they don't need deep codebase context.
- **Planner**: explores and creates/refines td tasks. Use when you lack the context yourself.
- **Tester**: writes or runs tests when that's a meaningful chunk of work on its own.

## Core loop

1. **Plan** — get to scoped td tasks, however that's cheapest.
2. **Implement** — dependency order. Usually one story per agent, but batch stories into one agent when they're tightly coupled, touch the same files, or are small enough that splitting them costs more than it buys. Don't parallelize agents over overlapping files.
3. **Review** — at meaningful boundaries. A batch review over several related stories is often better than per-story review: the reviewer sees the integrated result instead of fragments. Group by coherent user-facing or subsystem outcome. Keep security-sensitive changes, destructive migrations, and production deploys in their own review.
4. **Fix and re-review** — targeted fixes, then re-review the batch. One review plus one rejection cycle is usually enough; escalate further only for genuine P0 findings and file the rest as follow-up tasks.
5. **Close** — see below.
6. **Wrap up** — integration check if the work spans batches, then summarize.

Re-read td state between steps rather than carrying it in memory. If the user adds tasks mid-flight, re-read the epic and slot them into the dependency graph.

## Closing tasks

td's default trusted mode wants an independent review, and gives you an audited escape hatch when that isn't practical:

```bash
td approve <id> --reason "..."                    # independent reviewer
td approve <id> --self-review --reason "..."      # you reviewed it yourself; stamped self_review for audit
```

The orchestrator gets flagged as implementation-involved once it spawns an implementer, so plain `td approve` will refuse. If a sub-agent reviewer actually reviewed the work, that review is real and independent — record it and close with `--self-review --reason "reviewed by <agent/batch>: <summary>"`. The flag is an audit stamp, not a confession.

What's not okay: spinning up a throwaway session to make a review *look* independent, or self-reviewing work nobody read. If a project pins `review_policy_mode=delegated|strict`, the escape hatch is gone by design — use `td log` verdicts and let another session close.

## Proof

Capture proof by default — it's what makes "done" checkable later. Decide per task whether it earns its keep:

- **Worth it**: UI changes (screenshot), anything where the test suite doesn't demonstrate the actual user-visible outcome, infra/deploy work, bug fixes where the repro matters.
- **Skip it**: well-tested code with no UI surface and no behavior a test doesn't already assert. Passing tests recorded in the td log are the proof. Say so rather than manufacturing a ceremonial proof task.

When you do capture it:

1. Update the implementation task / epic / phase with the result.
2. Create `Proof: <thing proved>` as a child task with the `proof` label.
3. Put the artifact — or a direct path to it — in the description. Name the exact artifact up front: not "capture proof" but "screenshot of ActivityPanel showing 3 block types at `/tmp/rich-blocks-proof.png`" or "output of `go test ./internal/modules/planner/...`". Vague proof tasks get skipped or produce useless output.
4. Do it before final handoff, so proof lives in td rather than only in chat.

If the user explicitly asks to prove or verify work, treat proof as part of completion, not an optional follow-up.

## Practical notes

- Scale ceremony to the project. Personal and LAN-only work can use broad batches and light gates; public, multi-user, security-sensitive, or production work deserves narrower batches and stronger ones.
- Every commit references a td task id.
- Include lint/type-check in implementer prompts where the project has one (e.g. `svelte-check` for Svelte frontends).
- If blocked, `td log --blocker` and move to the next unblocked task.
- Feedback and verdicts go through `td log` / `td approve` / `td reject` — externalize state so it survives compaction.

## On compaction / handoff

Before context runs out or if pausing:

```bash
td handoff <current-task-id> \
  --done "completed tasks and outcomes" \
  --remaining "pending tasks in order" \
  --decision "key decisions made" \
  --uncertain "open questions"
```

Then tell the user: "Resume with `/orchestrate td-<id>`."

Include this in every sub-agent prompt: "If your context is compacted, read td state with `td context <id>` and continue from there. The process is: plan → implement in dependency order → independent review at batch boundaries → targeted fixes → close."
