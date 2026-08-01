---
name: orchestrate
description: Orchestrate development work through sub-agents using td for state. Use when given a td task ID, text idea, markdown plan, or td epic to execute through plan-implement-review loops, or when asked to triage the pending review queue.
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
| "review what's pending" | No target; user wants the queue triaged | `td reviewable`, then run the review loop below |

If the work needs more than one task, create an epic and link the sub-tasks to it. `td next` and `td critical-path` are the fastest way to pick an order when the dependency graph isn't obvious.

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

## Reviewing

Whether you are reviewing this loop's own output or triaging a queue someone else filled (`td reviewable`), the shape is the same: gather, review in parallel, act sequentially.

Give a reviewer the **contract**, not just the diff — the acceptance criteria, the plan or design doc the work was built against, and the quality gates. A reviewer with only the diff can tell you the code is coherent; one with the contract can tell you it is *wrong*. Ask it to falsify, not to admire.

Reviewers report a verdict, and you act on it:

| Verdict | What you do |
|---------|-------------|
| **Clean** | Approve (see Closing tasks) |
| **Obvious fix** | Fix it now — file the bug task first so it's tracked, fix, re-review |
| **Needs tests** | File a task naming exactly what needs testing and why |
| **Bigger issue** | File a task: what's wrong, where, suggested approach, context from the review |
| **Unclear** | Ask the user. Don't approve or reject code nobody understands |

Every task you file has to survive a cold pickup — enough context that an agent with none of this conversation can act on it. Vague tasks get skipped or produce useless output.

Parallelize independent reviews; serialize the acting, so two fixes don't collide in the same file. Once the fixes land, scan for in-progress tasks they resolved and close them rather than leaving them stale.

A reviewer sub-agent prompt wants: task ids and repo path, the diff range, the contract, the gates to run, and an instruction to report a verdict per the table above with a concrete reproduction for each finding. A finding without a reproduction is not a finding.

## Working the tools well

- Spawn independent agents in one message so they run concurrently instead of in sequence.
- Reuse an agent that already has the context for its own follow-up fixes rather than spawning a fresh one that has to re-derive everything.
- Size prompts to the job. Implementers need real context; reviewers mostly need the diff, the acceptance criteria, and the quality gates. Short reviewer prompts are cheaper and no worse.
- Prefix each sub-agent prompt with its role, the td task IDs, the repo path, a distinct `TD_CONTEXT_ID` to export, and an instruction to `td log` progress. Roles are labels, not a fixed roster — implementer, reviewer, planner, tester, whatever the work actually needs. The context id is what lets a reviewer close its own verdict (see Closing tasks).
- Include the project's lint and type-check commands in implementer prompts (e.g. `svelte-check` for Svelte frontends).
- Re-read td state between steps instead of carrying it in your head. If the user adds tasks mid-flight, re-read the epic and slot them into the dependency graph.
- Every commit references a td task id: `feat|fix|chore: <summary> (td-XXXXXX)`.
- If blocked, `td log --blocker` and move to the next unblocked task.
- Feedback and verdicts go through `td log` / `td approve` / `td reject`, so state survives compaction.

The td CLI is self-documenting — `td usage`, `td <command> --help`. Look there rather than guessing at flags.

## Closing tasks

td's default trusted mode wants an independent review, and its flags exist so the recorded history matches what actually happened. Pick by who did what — not by which flag gets past the check:

```bash
# The reviewing sub-agent has its own session (TD_CONTEXT_ID): let IT close.
td approve <id> --reason "..."                     # run BY the reviewer

# You delegated the implementation and reviewed it yourself.
td approve <id> --reason "..."                     # you are not the implementer-of-record

# You implemented it and a sub-agent reviewed it.   ← the common orchestrator case
td approve <id> --reviewed-by "reviewer sub-agent"  # no --reason needed; the name IS the substance

# You implemented it and nobody else looked.
td approve <id> --self-review --reason "..."       # stamped self_review for audit
```

**Give each sub-agent its own `TD_CONTEXT_ID`** (`reviewer-<taskid>`, `impl-<taskid>`) before it runs any `td` command, and let the reviewer close its own findings or record them with `td approve --record-only --reason "..."`. That makes the independence *mechanically verified* instead of asserted, and it costs one environment variable. Prefer it.

**`--reviewed-by` is the fallback when that isn't available** — a sub-agent sharing your session still did the review, and naming it is more honest than claiming a self-review you did not perform. Identify the reviewer however is useful and true: `"code-reviewer sub-agent"`, `"sub-agent 2 (adversarial review)"`, or just `"sub-agent"`. td does not verify the name; it is an attestation.

If you find yourself blocked at `td approve` because you are the implementer-of-record, that is the signal to pick one of the two honest paths — not to leave the story sitting in `in_review`. A story that is implemented, reviewed, and green should not need the user to close it by hand.

What's not okay: naming a reviewer that did not review (worse than an honest `--self-review`, because it reads as independent in the audit trail), spinning up a throwaway session to make a review *look* independent, or approving work nobody read. If a project pins `review_policy_mode=delegated|strict`, self-review is blocked by design — record the verdict with `td log` and let another session close.

See `td approve --help` and `docs/multi-agent-sessions.md` in the td repo for the full mode table.

## Proof

Capture proof by default — it's what makes "done" checkable later. Decide per task whether it earns its keep:

- **Worth it**: UI changes (screenshot), anything where the test suite doesn't demonstrate the actual user-visible outcome, infra/deploy work, bug fixes where the repro matters.
- **Skip it**: well-tested code with no UI surface and no behavior a test doesn't already assert. Passing tests recorded in the td log are the proof. Say so rather than manufacturing a ceremonial proof task.

When you do capture it, put it in td rather than only in chat: update the implementation task or epic with the result, and create a `Proof: <thing proved>` child task with the `proof` label. Name the exact artifact up front — not "capture proof" but "screenshot of ActivityPanel showing 3 block types at `/tmp/rich-blocks-proof.png`" or "output of `go test ./internal/modules/planner/...`". Vague proof tasks get skipped or produce useless output.

If the user explicitly asks to prove or verify work, proof is part of completion, not an optional follow-up.

## Scaling

Match the gates to the stakes. Personal and LAN-only work can run broad batches and light gates. Public, multi-user, security-sensitive, or production work deserves narrower batches and stronger ones. Don't spend a security-grade process on a personal script, and don't ship a payments change on a personal-script process.

## On compaction / handoff

td is the memory, so write to it before you need it: `td log` progress and `td log --decision` the reasoning as you go. A decision recorded after compaction is a decision reconstructed.

Before context runs out or if pausing:

```bash
td handoff <current-task-id> \
  --done "completed tasks and outcomes" \
  --remaining "pending tasks in order" \
  --decision "key decisions made" \
  --uncertain "open questions"
```

Be honest in `--done`; "mostly working" is not done, and the next session pays for the difference. For work spanning several tasks, `td ws start "<name>"` / `td ws tag <ids>` / `td ws handoff` captures the whole set at once.

Then tell the user: "Resume with `/orchestrate td-<id>`."

Include this in every sub-agent prompt: "If your context is compacted, read td state with `td context <id>` and continue from there."
