---
name: write-plans
description: Write and update durable project, implementation, migration, and architecture plans. Use when creating a new plan document, revising an existing plan, choosing where a plan belongs in a repository, or splitting a large plan into an indexed set of documents.
---

# Write Plans

Write plans as current instructions for future work, not as narratives of how the plan evolved.

## Preserve the Current State

- State the plan as it is now. When facts or decisions change, replace the outdated text instead of annotating the old text inline.
- Avoid historical comparisons such as “previously,” “now,” “changed from,” or “unlike the original plan” unless that history is necessary to execute or understand the work.
- Rely on version control for history. If essential context would otherwise be lost, add a very brief changelog at the bottom of the plan.
- Keep one clearly controlling plan. Remove or update stale guidance and references that could send an agent to an obsolete plan.

## Follow Repository Conventions

Inspect the repository before choosing a location or structure. Follow its existing plan directories, indexes, naming patterns, and status conventions.

If the repository has no convention, use:

```text
docs/plans/
├── planning/
├── active/
├── implemented/
└── deprecated/
```

Choose the directory that describes the plan's current state. Add another status directory when none of these categories fits. When moving a plan between states, update indexes and inbound references so its canonical location remains discoverable.

## Keep Plans Usable

- Make scope, intended outcome, important decisions, work sequence, dependencies, and acceptance evidence explicit when they matter.
- Distinguish settled decisions from unresolved questions. Do not present assumptions or proposals as established facts.
- Prefer a concise, navigable plan over an exhaustive narrative.
- If a plan would flood an agent's context, turn it into a directory with a concise index and focused supporting documents. Make the index identify the controlling document, recommended reading order, and purpose of each file.
- Do not include developer-time estimates unless the user explicitly requests them.
- Optionally include rough story or epic sizing when it helps communicate relative scope; sizing is not required.

## Update Existing Plans

Read the whole affected plan and its index before editing. Rewrite impacted sections into a coherent current-state document, then check for contradictions, stale links, duplicate authorities, and status mismatches across the plan set.
