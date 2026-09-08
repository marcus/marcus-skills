---
name: project-standards
description: The standards every agent follows when working in one of Marcus's projects — git and GitHub defaults, language order and stacks, td and docs layout, Sidecar and comms awareness, living plans, adapter seams, UI and icon libraries, and how to communicate decisions. Load at the start of any work in a managed repo, before planning or writing code, and whenever choosing a language, stack, layout, or workflow for a new project.
---

# Project Standards

These are the house rules for every project Marcus manages. They bind regardless of harness or model. When a project's own AGENTS.md or CLAUDE.md is more specific, follow it; when it is silent, follow this.

## Always

- **Harness- and model-agnostic.** Nothing assumes Claude Code, Codex, Gemini, or one model vendor. Building for one harness is a decision to raise first.
- **Local-first, inspectable.** Prefer tools and layouts reachable from the machine without a proprietary control plane. Prefer text formats (JSONL, markdown) an agent can read, diff, and repair.
- **Commit as you go.** Don't leave large uncommitted piles.
- **Push freely.** Private repos: push to GitHub as normal backup while working. Public repos: also fine unless told not to.
- **Private by default.** New work gets a git repo and a **private** GitHub repo, without being asked, unless told to go public.
- **Land the branch.** Merge feature-branch work back to `main` unless asked to leave it. Worktrees for parallel work; `main` directly is fine early on or for small changes.
- **Track work in `td`.** In every repo. `td usage --new-session -q` to orient, `td start`, `td log`, `td handoff`, `td review`, then approve with a stated reviewer.
- **Finish in line.** Closing a ticket by spawning "should-do" follow-ups is an anti-pattern. Obvious next work that belongs with the change gets done now. Follow-up td items are only for non-obvious, optional, or genuinely deferred work that would be fine if it never happened.
- **Clean as you go.** Every agent owns hygiene. Noisy logs, flaky tests (even pre-existing), awkward build steps, worktree friction, failing linters, oversized files: surface it **and fix it**, not only file a note.
- **Adapters at seams that churn.** AI providers, agent harnesses, databases, transport, renderers. One interface, one boring default implementation, so a swap is "write a new adapter", never "refactor the app". Reference: `~/code/backstage` (Ruby).
- **Modular from day one.** Even small projects. Assume growth; don't wait for pain to introduce structure.
- **Agents are first-class users.** Every owned capability has a non-interactive CLI or API path with structured output. UI is a projection of that, never a privileged path. See the `surface-parity` skill.

## Sibling skills

Use these by name; they carry the detail this file only points at.

| Intent | Skill |
|---|---|
| Building, refactoring, reviewing | `pragmatic-engineering` |
| Plans as living documents | `write-plans` |
| Sub-agent orchestration via td | `orchestrate` |
| TUI screens, before inventing in-app UI | `tui-design` |
| Owned capabilities across UI, CLI, API, MCP | `surface-parity` |
| Icons | `roc-icons` |
| SvelteKit + Svelte 5 reference | `sveltekit-latest` |

## Language preferences

| Order | Language | When |
|---|---|---|
| 1 | **Go** | New projects by default |
| 2 | **JavaScript / TypeScript** | When the problem wants a web or UI stack (often) |
| 3 | **Ruby** | Quicker projects, or systems primarily for Marcus |
| 4 | **Bash** | Where a shell solution is enough; actively preferred there |
| 5 | **Rust** | When performance is essential |
| 6 | **Python** | Allowed, not preferred |
| — | Anything else | Discuss first |

### Go stack

Match `tasks`, `td`, `sidecar`, `recall`, `comms`. Canonical reference is **`~/code/sidecar`**; `~/code/comms` is the leanest current copy of the same shape.

- `Makefile` with `build`, `install`, `install-local` (or equivalent) so the **local branch or worktree installs in one command**. Sidecar adds `install-worktree` and `use-homebrew` to switch between a dev build and the tap.
- **goreleaser v2** with a **Homebrew tap** target; `make release`, `release-dry-run`, `release-tap`.
- GitHub Actions: a CI workflow (`go-ci.yml` or `ci.yml`) plus `release.yml` triggered on `v*` tags, which verifies the tag against live `main` before publishing. Keep Actions aligned with how the repo actually releases.
- `go-version-file: go.mod` everywhere; toolchain via `mise`.

### JavaScript / TypeScript stack

- **SvelteKit + TypeScript.**
- **SQLite** by default; **Postgres** when there's a real reason. Say what the reason was.
- UI: the **Linear design system** for now (`linear-design-patterns`); expect a house style later.

### Storage progression

JSONL → SQLite → Postgres. Start at the simplest store that works; move up on concrete pain (concurrent writers, query complexity, volume, multi-host), and say what the pain was. All persistence behind one narrow store interface, no store-specific features in business logic.

## Docs layout

Default to the Clara / td shape: `docs/` with types such as `plans/` and `guides/`, and under those `active/`, `implemented/`, `deprecated/`.

Plans are living documents (`write-plans`): move them through those folders as work progresses, keep them updated in brief informal strokes, record handoffs in both `td` and the plan, and allow a short changelog at the bottom. Don't litter the body with "decided / changed / updated" archaeology.

## Runtime environment

- **Sidecar.** Always check whether you are inside Sidecar: `sidecar agents` lists what you can do. If yes, use its agent commands to open files, message agents, create worktrees, and present what you're working on (`sidecar open`, `sidecar layout`, `sidecar create worktree`). Never auto-answer another agent's approvals.
- **comms.** System-wide agent-to-agent messaging: `comms join`, `publish`, `send @handle`, `inbox --unread`. Prefer it when agents need to talk to each other.
- **TUI work.** Use the `tui-design` studio before inventing in-app TUI so designs stay consistent.
- **Clippy.** How Marcus sends screenshots from the laptop. Know it exists; no deep expertise needed.

## Tool surface

The cross-project toolbox. Home-only tools live in Clara's `profile/TOOLS.md`; this is the slice every managed project should know about.

| Tool | Use it for |
|---|---|
| `td` | Engineering issues, resolved per git repo. Always. |
| `tasks` | Marcus's personal GTD. Something you noticed rather than were asked for goes in as `tasks propose "text" --note "why"`, never `capture`. |
| `sidecar` | Agent cockpit: shells, worktrees, panes, agent messaging. `sidecar agents` for the surface. |
| `comms` | Async agent-to-agent messaging across harnesses. |
| `recall` | Retrieval across the corpus, project docs, tasks, td, and the catalog when you don't know which source holds the answer. Keywords, not sentences. |
| `ongoing` | The project catalog: what is managed, its stacks, intent, and attention. `ongoing show <project>`, `ongoing stacks --outdated`. |
| `mise` | The single surface for language runtimes and CLI tools. Wrong binary or version? Start here. |
| `gh` | GitHub. Create repos private by default. |
| `naturally` | Run prose that anyone other than Marcus will read through it. |
| `roc` | Icon library at `~/code/roc`. Add, publish, and improve icons freely (`roc-icons`). |

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
