# Agent-guidance modernization inventory and rollout plan

## Decision

Normalize legacy agent-workflow instructions in Marcus-owned repositories to
the current `orchestrate` skill and td v3 guidance. The new common posture is:

- Guidance is a set of defaults, not a ceremony or fixed agent roster.
- Use judgment about whether a change needs td tracking, worktrees, delegation,
  proof, or a plan.
- Keep one hard completion gate: every story is reviewed by someone other than
  its author before it closes. Record the review truthfully through td.
- Keep project-specific safety, product, test, release, and data-integrity
  rules. This project layer is not being weakened.
- Beads is retired everywhere. Remove its instructions and references rather
  than preserving it as an alternative tracker.

The canonical shared text is the versioned block in
`td/internal/agent/instructions.go` (`InstructionVersion = 3`). For execution
workflow choices, link to or invoke `skills/orchestrate/SKILL.md`; do not copy
its long-lived operational detail into every repository.

## Scope and inventory

The inventory used root-level `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `GEMINI.md`,
`GROK.md`, `COPILOT.md`, `CURSOR.md`, and `WINDSURF.md` files in Git project
roots under `/Users/marcus/code`, excluding vendored dependencies. A file is a
candidate when it imposes an old td/session ritual, mandates task creation for
every request, fixes an implementer/reviewer/orchestrator sequence, or contains
duplicated harness-specific workflow guidance.

### P0: active guidance with a materially rigid or misleading workflow

| Project | Files | Finding | Planned correction |
| --- | --- | --- | --- |
| `marcus-skills` | `AGENTS.md` | Mandatory session bootstrap is the source most likely to re-spread the old rule. | Replace it with the v3 marked td block and add a short pointer to `orchestrate` for multi-step work. Retain browser-proof guidance. |
| `snapshot` | `AGENTS.md` | Mandates one story per feature, individual sub-agent implementation, epic-only review, reviewer session rotation, and reviewer-owned bookkeeping. | Replace the entire process section with outcome-based guidance: coherent batching is a judgment call; every story is covered by a non-author review before close; td records real attribution. Keep the offer-page instructions. |
| `sidecar` | `AGENTS.md` (also `GEMINI.md` symlink) | Requires creating td task(s) before work when none is supplied. | Install v3 block in the single source file and change the task rule to tracking proportional to substantive work. Preserve UI/startup rules. |
| `slinky` | `CLAUDE.md` | Requires a forced new td session and td task management before all coding. | Replace with v3 block; preserve the product-specific guidance. |
| `muse` | `CLAUDE.md` | Mandates td bootstrap while separately declaring Beads the default tracker. | Remove Beads entirely, standardize on a canonical `AGENTS.md` with the brief td v3 block, and retain the project-specific guidance. |
| `nightshift` | `AGENTS.md`, `CODEX.md` | Mandatory bootstrap plus duplicate Codex instructions with a stale `/Users/marcusvorwaller/...` path. | Make `AGENTS.md` the shared source with v3 block; reduce `CODEX.md` to a pointer or remove it if no Codex-only behavior remains. |
| `zeroshot` | `AGENTS.md`, `CLAUDE.md` | Both duplicate mandatory bootstrap; the file also contains historical notes that need separation from active rules. | Keep one canonical shared workflow block, remove duplicate startup mandates, and move historical incident notes to a dated docs/changelog location if still useful. |
| `marcuspictures` | `AGENTS.md`, `CLAUDE.md` | Two harness-specific copies of the mandatory session ritual. | Make `AGENTS.md` canonical, install v3 there, and reduce `CLAUDE.md` to a pointer or keep only genuine Claude-specific content. |

### P1: simple legacy bootstrap copies

These have the same unconditional `td usage --new-session` pattern but no
additional rigid orchestration. Replace the legacy stanza with the v3 marked
block, retaining all project-specific guidance after it.

- `betamax/CLAUDE.md`
- `carousel/AGENTS.md`
- `flowers/AGENTS.md`
- `haplab/AGENTS.md`
- `inquiry/AGENTS.md`
- `melville/AGENTS.md`
- `roc/AGENTS.md`
- `wordy/AGENTS.md`
- `year-in-review/CLAUDE.md`
- `perch/CLAUDE.md` (light-touch: it is not otherwise rigid, but should use the
  marked block for upgradeability)
- `clara-home/AGENTS.md` (light-touch: retain its repository-routing and
  proposal policy; only replace the unconditional bootstrap sentence)
- `td-watch/AGENTS.md` (light-touch: retain all Osprey, proof, lint, and
  main-branch rules; change only the startup ritual and make the pre-review
  checklist conditional on work actually reaching review)

### P2: inherited guidance and stale worktrees — inventory only

These are Git worktrees of a parent project, not separate projects. Do not edit
or update them in this rollout. They are cleanup candidates for Marcus to
inspect separately.

- td worktrees: `td-changelog-synth-nightshift`,
  `td-commit-normalize-20260504`, `td-docs-backfill-notes`,
  `td-release-note-drafter`, `td-wt-02ae9f`, `td-wt-b76671`,
  `td-wt-integrate-f867ee`, `td-wt-monitor-integrity`
- nightshift worktree: `nightshift-commit-msg-normalizer-v3`
- perch worktree: `perch-commit-normalize-20260414`
- roc worktrees: `roc-commit-normalize`, `roc-release-notes-drafter`

The two roc worktrees also contain an "always use the sub-agent pattern" for
batch icon generation. That instruction belongs in the parent `roc` policy
review: keep any asset-quality requirements, but replace the fixed role/agent
count prescription with a safe batching constraint (no overlapping SVG edits;
independent review before close).

### Not rollout targets

Do not modify third-party/upstream or nested documentation merely because it
uses a guidance-like name (for example OpenClaw documentation templates,
Penpot subprojects, `node_modules`, `vendor`, virtual environments, fixtures,
and source files with `agents` in their path). The scan found no root
`GEMINI.md` or `GROK.md` requiring a separate modernization; `sidecar`'s
`GEMINI.md` is already a symlink to `AGENTS.md`.

## Implementation sequence

1. **Land the shared source first.** Update `marcus-skills/AGENTS.md` and
   confirm `skills/orchestrate/SKILL.md` and td's `InstructionText` agree on
   terminology: judgment-led tracking, proportional proof, truthful review
   attribution, and no synthetic independence.
2. **Use a single canonical filename.** Rename a sole `CLAUDE.md` (or similar)
   to `AGENTS.md`; when a harness-specific filename existed beforehand, replace
   it with a relative symlink to `AGENTS.md` (for example,
   `CLAUDE.md -> AGENTS.md`). Do not add new harness-specific aliases where
   none existed.
3. **Migrate P0 one project at a time with GPT Terra sub-agents.** Each agent
   works in only its assigned repositories, removes Beads where present,
   preserves real constraints, and adds only brief shared guidance. No migration
   helper or bulk rewrite script will be created.
4. **Batch P1 by low-conflict repo.** Apply the reviewed stanza replacement,
   then use a final read-only scan to prove no legacy mandatory-bootstrap
   pattern remains in the selected files.
5. **Leave worktrees untouched.** Record them as cleanup candidates only; do
   not rebase, merge, update, or prune them as part of this work.
6. **Commit and push deliberately.** Before editing a repository, inspect
   `git status --short`, branch, and upstream. Stage only the intended guidance
   files and commit them separately. If the repository is on `main` or `master`
   and its remote is already current before the change, push the scoped commit
   after review. If it begins on another branch or is behind/diverged, report it
   without pushing for a case-by-case decision.
7. **Verify and review.** For each repository, run its applicable docs lint or
   focused checks, inspect rendered guidance, and have an independent reviewer
   check the changed files and scoped commit. Run a final cross-repo
   scan for legacy phrases and duplicate conflicting guidance.

## Acceptance criteria

- Every migrated project has exactly one canonical `AGENTS.md` workflow source;
  a pre-existing secondary harness filename is a relative symlink to it, and no
  new aliases are added.
- Canonical td guidance uses the complete v3 marked block, so later td upgrades
  are safe and mechanical.
- No migrated file says a session must be created at every conversation start,
  every request must become a td task, every story must get a dedicated
  sub-agent, or that review must follow one fixed ownership sequence.
- No project loses its real safety, data, test, release, UI-proof, or
  branch/worktree constraints.
- No migrated project references or instructs use of Beads (`bd`).
- Every commit stages only the guidance paths assigned to that repository;
  pre-existing unstaged work is left untouched.
- Instructions retain the non-negotiable outcome: a story receives an honest
  review by someone other than its author before closing, with td attribution
  matching reality.
- The final inventory report has zero unclassified root guidance files and
  explicitly lists all intentionally deferred worktrees/upstream files.

## Risks and decisions to make during execution

- A repository may have a PR workflow or other project-specific process. Keep
  it where it is a real product/release constraint, but do not add td
  boilerplate merely for uniformity.
- `td`'s current `AnyFileHasTDInstructions` treats any `td usage` text as
  already configured. This is why each legacy stanza needs a deliberate,
  reviewed edit rather than an automatic upgrader.
- Do not mass-rewrite every occurrence of `must` or `always`: product safety
  invariants are often correctly mandatory. This rollout changes agent-process
  rigidity, not engineering standards.
