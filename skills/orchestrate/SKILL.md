---
name: orchestrate
description: Orchestrate development work through sub-agents using td for state. Use when given a td task ID, text idea, markdown plan, or td epic to execute through plan-implement-review loops.
---

# Orchestrate

Run multi-step development work through sub-agents, with `td` as the durable state store.

This is guidance, not a protocol. You know your tools and the shape of the work in front of you better than this file does. Optimize for efficiency and correctness — not for looking like you followed steps.

**The one rule that isn't negotiable: every story gets reviewed by something other than what wrote it, before it closes.** Everything on the rest of this page is a default you should feel free to beat.

## Classify input

| Input | Detect | Bootstrap |
|-------|--------|-----------|
| td task | `td-[a-f0-9]+` | `td show <id>` + `td context <id>`, then implement |
| td epic / multiple IDs | Multiple td IDs or user says "epic" | `td show` each, plan execution order |
| Text idea | No td ID, plain text | Create td task(s), then implement |
| Markdown plan | Structured markdown with steps | Convert to td tasks, then implement |

If the work needs more than one task, create an epic and link the sub-tasks to it.

## Your role

You hold the plan, keep state in td, and spend your context on coordination rather than on code.

- **Planning**: do it yourself when you already have the context. Spawning a planner to rediscover what you just read burns a whole window for nothing. Delegate planning when the area is large or unfamiliar.
- **Implementation**: delegate by default. It protects your context and it's what makes the review independent. Small mechanical edits you've already diagnosed are fine to do directly.
- **Review**: delegate, always. Never review code you wrote.

## Batching is your call

How you slice work across agents is the main lever you have on both speed and quality. Use it. Nobody is counting agents.

**Implementation.** Group stories that touch the same files, share a design decision, or are small enough that a separate agent costs more than it saves. Split what's genuinely independent so it can run concurrently. The one hard constraint: don't run parallel agents over overlapping files — serialize them, or give each its own worktree.

**Review.** Batch these the same way. One reviewer over a coherent feature usually finds more than several reviewers over the same work in fragments, because it sees the integrated result and can spot the seams. Narrow the batch when a missed finding is expensive: security-sensitive changes, destructive migrations, production deploys, anything public-facing.

A batch review still has to actually cover every story in it. Name the stories and the diff range in the reviewer's prompt so "reviewed" means someone read that story's changes, not that it rode along inside a batch.

**Rejections.** Fix and re-review, but converge. One review plus a fix cycle usually gets there; past that, land the P0 findings and file the rest as follow-up tasks rather than looping.

## Working the tools well

- Spawn independent agents in one message so they run concurrently instead of in sequence.
- Reuse an agent that already has the context for its own follow-up fixes rather than spawning a fresh one that has to re-derive everything.
- Size prompts to the job. Implementers need real context; reviewers mostly need the diff, the acceptance criteria, and the quality gates. Short reviewer prompts are cheaper and no worse.
- Prefix each sub-agent prompt with its role, the td task IDs, the repo path, and an instruction to `td log` progress. Roles are labels, not a fixed roster — implementer, reviewer, planner, tester, whatever the work actually needs.
- Include the project's lint and type-check commands in implementer prompts (e.g. `svelte-check` for Svelte frontends).
- Re-read td state between steps instead of carrying it in your head. If the user adds tasks mid-flight, re-read the epic and slot them into the dependency graph.
- Every commit references a td task id: `feat|fix|chore: <summary> (td-XXXXXX)`.
- If blocked, `td log --blocker` and move to the next unblocked task.
- Feedback and verdicts go through `td log` / `td approve` / `td reject`, so state survives compaction.

## Closing tasks

td's default trusted mode wants an independent review, and gives you an audited escape hatch when that isn't practical:

```bash
td approve <id> --reason "..."                    # independent reviewer
td approve <id> --self-review --reason "..."      # you reviewed it yourself; stamped self_review for audit
```

Sub-agents run in their own sessions, so the orchestrator is not the implementer-of-record for work it delegated — plain `td approve <id> --reason "..."` works, no flag needed.

Use `--self-review` when you're closing something you implemented yourself, like a nit-fix mid-loop. It requires `--reason` and stamps the review row for audit. It's a disclosure, not a confession; the point is that the record matches reality.

What's not okay: spinning up a throwaway session to make a review *look* independent, or approving work nobody read. If a project pins `review_policy_mode=delegated|strict`, self-review is blocked by design — record the verdict with `td log` and let another session close.

## Proof

Capture proof by default — it's what makes "done" checkable later. Decide per task whether it earns its keep:

- **Worth it**: UI changes (screenshot), anything where the test suite doesn't demonstrate the actual user-visible outcome, infra/deploy work, bug fixes where the repro matters.
- **Skip it**: well-tested code with no UI surface and no behavior a test doesn't already assert. Passing tests recorded in the td log are the proof. Say so rather than manufacturing a ceremonial proof task.

When you do capture it, put it in td rather than only in chat: update the implementation task or epic with the result, and create a `Proof: <thing proved>` child task with the `proof` label. Name the exact artifact up front — not "capture proof" but "screenshot of ActivityPanel showing 3 block types at `/tmp/rich-blocks-proof.png`" or "output of `go test ./internal/modules/planner/...`". Vague proof tasks get skipped or produce useless output.

If the user explicitly asks to prove or verify work, proof is part of completion, not an optional follow-up.

## Scaling

Match the gates to the stakes. Personal and LAN-only work can run broad batches and light gates. Public, multi-user, security-sensitive, or production work deserves narrower batches and stronger ones. Don't spend a security-grade process on a personal script, and don't ship a payments change on a personal-script process.

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

Include this in every sub-agent prompt: "If your context is compacted, read td state with `td context <id>` and continue from there."
