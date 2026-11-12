---
name: project-standards
description: The standards every agent follows when working in one of Marcus's projects — git and GitHub defaults, language rings and stacks, storage and adapter seams, td and docs layout, Sidecar and comms awareness, living plans, UI and icon libraries, web apps on phones, and how to communicate decisions. Load at the start of any work in a managed repo, before planning or writing code, and whenever choosing a language, stack, layout, or workflow for a new project.
---

# Project Standards

These are the house rules for every project Marcus manages. They bind regardless of harness or model. When a project's own AGENTS.md or CLAUDE.md is more specific, follow it; when it is silent, follow this. They are defaults, not laws, but deviating from one is a decision worth stating out loud.

## Always

- **Harness- and model-agnostic.** Nothing assumes Claude Code, Codex, Gemini, Grok, Cursor, or one model vendor; Clara is the seam that keeps them swappable. Building for one harness is a decision to raise first.
- **Local-first, inspectable.** Prefer tools and layouts reachable from the machine without a proprietary control plane. Prefer text formats (JSONL, markdown) an agent can read, diff, and repair.
- **Commit as you go.** Don't leave large uncommitted piles.
- **Push freely.** Private repos: push to GitHub as normal backup while working. Public repos: also fine unless told not to.
- **Private by default.** New work gets a git repo and a **private** GitHub repo, without being asked, unless told to go public.
- **Land the branch.** Merge feature-branch work back to `main` unless asked to leave it. Worktrees for parallel work; `main` directly is fine early on or for small changes.
- **Track work in `td`.** In every repo. `td usage --new-session -q` to orient, `td start`, `td log`, `td handoff`, `td review`, then approve with a stated reviewer. A fresh sub-agent that the implementer spawns, in its own td session, counts as independent. After approval, carry the work through to merge and install unless the repo's AGENTS.md says otherwise.
- **Finish in line.** Closing a ticket by spawning "should-do" follow-ups is an anti-pattern. Obvious next work that belongs with the change gets done now. Follow-up td items are only for non-obvious, optional, or genuinely deferred work that would be fine if it never happened.
- **Clean as you go.** Every agent owns hygiene. Noisy logs, flaky tests (even pre-existing), awkward build steps, worktree friction, failing linters, oversized files: surface it **and fix it**, not only file a note.
- **Adapters at seams that churn.** Model providers, agent harnesses, storage, transport, renderers, notifiers, schedulers. One interface, one boring default implementation, so a swap is "write a new adapter", never "refactor the app". Reference: `~/code/backstage` (Ruby).
- **Modular from day one.** Even small projects. Assume growth; don't wait for pain to introduce structure.
- **Agents are first-class users.** Every owned capability has a non-interactive CLI or API path with structured output. UI is a projection of that, never a privileged path. Ask "how does an agent invoke this?" before "where does this button go?" See the `surface-parity` skill.

## How much of this is prescription

These rules set direction and leave the craft to you. Agents plan, orchestrate, review and write framework code well without a playbook, so nothing here prescribes how to do those things. Reach for current official documentation when a detail matters. The one companion skill is `surface-parity`, for keeping owned capabilities aligned across UI, CLI, API and MCP.

## Language preferences

This table is generated from the Ongoing catalog — `ongoing tech list --kind language`. Edit the
catalog (`ongoing tech set <slug> --ring <ring> --note "<when>"`), then regenerate with
`bun run ~/code/ongoing/scripts/render-project-standards.ts`; don't edit the rows by hand. The
ring says how much a language is the current default: **hot** is the default choice for new work,
**warm** is fine to keep using, **cool** needs a reason and expects to migrate off, **out** means
don't start new work on it.

<!-- ongoing:languages:start -->
| Language | Ring | When |
|---|---|---|
| **Go** | hot | New projects by default; td, tasks, sidecar, comms and recall are the reference shape. |
| **JavaScript / TypeScript** | hot | When the problem wants a web or UI stack, which is often. |
| **Bash** | warm | Where a shell solution is enough; actively preferred there. |
| **Python** | warm | The default for ML and model work; acceptable elsewhere when its ecosystem is the best fit. |
| **Rust** | warm | When performance is essential. |
| **Ruby** | cool | Nothing new starts in Ruby; existing Ruby projects such as clara carry on in it. |
<!-- ongoing:languages:end -->

Anything else: discuss first.

### Storage progression

JSONL → SQLite → Postgres. Start at the simplest store that works; move up on concrete pain (concurrent writers, query complexity, volume, multi-host), and say what the pain was. All persistence behind one narrow store interface, no store-specific features in business logic. Details: `references/storage.md`.

## References

- `references/stacks.md`: a Go or JS/TS project's build, install, release, CI, database or UI look.
- `references/storage.md`: designing or changing persistence.
- `references/web-apps-on-phones.md`: anything with a web front end, especially iOS home-screen apps, icons and link previews.
- `references/architecture-diagrams.md`: the repo has `docs/diagrams/fractal/`, or architecture, boundaries, major flows or planned capabilities change.

## Docs layout

Default to the Clara / td shape: `docs/` with types such as `plans/` and `guides/`, and under those `active/`, `implemented/`, `deprecated/`.

Plans are living documents: move them through those folders as work progresses, keep them updated in brief informal strokes, record handoffs in both `td` and the plan, and allow a short changelog at the bottom. Don't litter the body with "decided / changed / updated" archaeology.

## Runtime environment

- **Sidecar.** Always check whether you are inside Sidecar: `sidecar agents` lists what you can do. If yes, use its agent commands to open files, message agents, create worktrees, and present what you're working on (`sidecar open`, `sidecar layout`, `sidecar create worktree`). Never auto-answer another agent's approvals.
- **comms.** System-wide agent-to-agent messaging: `comms join`, `publish`, `send @handle`, `inbox --unread`. Prefer it when agents need to talk to each other.
- **TUI work.** Use the `tui-design` studio before inventing in-app TUI so designs stay consistent.
- **Clippy.** How Marcus sends screenshots from the laptop. Know it exists; no deep expertise needed.

## Tool surface

The cross-project toolbox. Home-only tools live in Clara's `profile/TOOLS.md`; this is the slice every managed project should know about. Generated from the Ongoing catalog — every technology that carries a tool surface (`ongoing tech export`). Edit it with `ongoing tech set <tool> --tool-surface "..."` and regenerate.

<!-- ongoing:tools:start -->
| Tool | Use it for |
|---|---|
| `comms` | Async agent-to-agent messaging across harnesses. |
| `fractal` | Repository-owned architecture models, interactive presentation and SVG/PNG exports. Skill: `~/code/fractal/skills/fractal/SKILL.md`. |
| `gh` | GitHub. Create repos private by default. |
| `mise` | The single surface for language runtimes and CLI tools. Wrong binary or version? Start here. |
| `naturally` | Run prose that anyone other than Marcus will read through it. |
| `ongoing` | The project catalog: what is managed, its stacks, intent, and attention. `ongoing show <project>`, `ongoing stacks --outdated`. |
| `recall` | Retrieval across the corpus, project docs, tasks, td, and the catalog when you don’t know which source holds the answer. Keywords, not sentences. |
| `roc` | Icon library at `~/code/roc`. Add, publish, and improve icons freely (`roc-icons`). |
| `sidecar` | Agent cockpit: shells, worktrees, panes, agent messaging. `sidecar agents` for the surface. |
| `tasks` | Marcus’s personal GTD. Something you noticed rather than were asked for goes in as `tasks propose "text" --note "why"`, never `capture`. |
| `td` | Engineering issues, resolved per git repo. Always. |
<!-- ongoing:tools:end -->

A common CLI that clara-ui agents on other machines (eagle, marcusbook) should reach needs one line in `~/code/clara-home/config/agent-tools.json`; clara-ui forwards it to aerie from the next session. See `~/code/clara-ui/docs/machines.md`.

## UI components and icons

Build crisp, reusable components. Prefer project-maintained component libraries, not one-off HTML or TUI controls and not random internet component packs. Icons come from `roc`.

## External-facing prose

Text that someone other than Marcus will read goes through `naturally` for tone.

## Communicating decisions to Marcus

Present choices as trade-offs and consequences, not API trivia.

- **User and product impact first.** If something makes the experience better or worse, say what changes and how.
- **Name the real decision.** Which of maintainability, performance, flexibility, security, operability move, and in which direction.
- **Jargon last.** No leading with method names, file names, or pattern labels. Marcus decides on how the software is used and maintained; implementation detail follows only if needed.
- **Multi-aspect is normal.** One decision often touches several parts; map that briefly rather than collapsing to option A/B.
