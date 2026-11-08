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
- **Track work in `td`.** In every repo. `td usage --new-session -q` to orient, `td start`, `td log`, `td handoff`, `td review`, then approve with a stated reviewer. A fresh sub-agent that the implementer spawns, in its own td session, counts as independent. After approval, carry the work through to merge and install unless the repo's AGENTS.md says otherwise.
- **Finish in line.** Closing a ticket by spawning "should-do" follow-ups is an anti-pattern. Obvious next work that belongs with the change gets done now. Follow-up td items are only for non-obvious, optional, or genuinely deferred work that would be fine if it never happened.
- **Clean as you go.** Every agent owns hygiene. Noisy logs, flaky tests (even pre-existing), awkward build steps, worktree friction, failing linters, oversized files: surface it **and fix it**, not only file a note.
- **Adapters at seams that churn.** AI providers, agent harnesses, databases, transport, renderers. One interface, one boring default implementation, so a swap is "write a new adapter", never "refactor the app". Reference: `~/code/backstage` (Ruby).
- **Modular from day one.** Even small projects. Assume growth; don't wait for pain to introduce structure.
- **Agents are first-class users.** Every owned capability has a non-interactive CLI or API path with structured output. UI is a projection of that, never a privileged path. See the `surface-parity` skill.

## How much of this is prescription

These rules set direction and leave the craft to you. Agents plan, orchestrate, review and write framework code well without a playbook, so nothing here prescribes how to do those things. Reach for current official documentation when a detail matters. The one companion skill is `surface-parity`, for keeping owned capabilities aligned across UI, CLI, API and MCP.

## Language preferences

This table is generated from the Ongoing catalog — `ongoing tech list --kind language`. Edit the
catalog (`ongoing tech set python --ring cool`), then regenerate; don't edit the rows by hand. The
ring says how much a language is the current default: **hot** is the default choice for new work,
**warm** is fine to keep using, **cool** needs a reason and expects to migrate off, **out** means
don't start new work on it.

<!-- ongoing:languages:start -->
| Language | Ring | When |
|---|---|---|
| **Go** | hot | New projects by default; td, tasks, sidecar, comms and recall are the reference shape. |
| **JavaScript / TypeScript** | hot | When the problem wants a web or UI stack, which is often. |
| **Bash** | warm | Where a shell solution is enough; actively preferred there. |
| **Ruby** | warm | Quicker projects, or systems primarily for Marcus. |
| **Rust** | warm | When performance is essential. |
| **Python** | cool | Allowed, not preferred. |
<!-- ongoing:languages:end -->

Anything else: discuss first.

### Go stack

Match `tasks`, `td`, `sidecar`, `recall`, `comms`. Canonical reference is **`~/code/sidecar`**; `~/code/comms` is the leanest current copy of the same shape.

- `Makefile` with `build`, `install`, `install-local` (or equivalent) so the **local branch or worktree installs in one command**. Sidecar adds `install-worktree` and `use-homebrew` to switch between a dev build and the tap.
- **goreleaser v2** with a **Homebrew tap** target; `make release`, `release-dry-run`, `release-tap`.
- GitHub Actions: a CI workflow (`go-ci.yml` or `ci.yml`) plus `release.yml` triggered on `v*` tags, which verifies the tag against live `main` before publishing. Keep Actions aligned with how the repo actually releases.
- `go-version-file: go.mod` everywhere; toolchain via `mise`.

### JavaScript / TypeScript stack

- **The latest stable SvelteKit and Svelte, with TypeScript.**
- **SQLite** by default; **Postgres** when there's a real reason. Say what the reason was.
- UI: **Apple's glass aesthetic**, as close to a modern Mac app as the web allows. `~/code/clara-ui/DESIGN.md` is the reference, with `~/code/studio/DESIGN.md` as a second example.

### Storage progression

JSONL → SQLite → Postgres. Start at the simplest store that works; move up on concrete pain (concurrent writers, query complexity, volume, multi-host), and say what the pain was. All persistence behind one narrow store interface, no store-specific features in business logic.

## Docs layout

Default to the Clara / td shape: `docs/` with types such as `plans/` and `guides/`, and under those `active/`, `implemented/`, `deprecated/`.

Plans are living documents: move them through those folders as work progresses, keep them updated in brief informal strokes, record handoffs in both `td` and the plan, and allow a short changelog at the bottom. Don't litter the body with "decided / changed / updated" archaeology.

## Architecture diagrams

Keep project-owned Fractal models in `docs/diagrams/fractal/` (`model.c4` and `fractal.json`).
When architecture, boundaries, major flows, or planned capabilities change, update the affected
model and scenes alongside the code. Preserve stable IDs and distinguish current behavior from
proposals. Use the [Fractal usage skill](~/code/fractal/skills/fractal/SKILL.md) to author, validate,
export, register the project in the local catalog, and open its diagram for Marcus. Keep the model
in the project repository and use Fractal's existing tools; model maintenance should not require
changes to Fractal core.

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

## UI components and icons

Build crisp, reusable components. Prefer project-maintained component libraries, not one-off HTML or TUI controls and not random internet component packs. Icons come from `roc`.

## Web apps on phones and when shared

Anything with a web front end (apps, games, tools, published pages) should feel native on a phone and look good when its link is shared.

- **Full height, no letterboxing.** Fill the whole screen where the content allows: `viewport-fit=cover`, full-height layouts (`100dvh` or fixed `inset: 0`), and safe-area insets for padding rather than dead bands top and bottom.
- **No selection by default.** Turn off text selection and the long-press callout on app chrome (`user-select: none`, `-webkit-touch-callout: none`, no tap highlight). Keep it where text is the point: documents, messages, code, anything someone would copy.
- **No accidental zoom in apps and games.** `touch-action: manipulation` on the page, `maximum-scale=1, user-scalable=no` in the viewport, and cancel Safari's `gesturestart`/`gesturechange` (it ignores `user-scalable`). Form fields at 16px or larger so focusing one doesn't zoom. Documents are different: images, diagrams and reading pages must stay zoomable.
- **Don't open the keyboard on arrival.** No autofocus on load on touch devices, so nobody lands on a screen half covered by the keyboard. Focus a field when the person taps it.
- **App icon and favicons from Studio.** Generate the icon with `studio image` (GPT Image, 1:1, full-bleed, opaque, no text), choose one that reads at 16px, and ship favicon `.ico`/32/16, a 180px `apple-touch-icon`, 192/512 icons and a `manifest.json` (served as JSON) with `apple-mobile-web-app-*` tags, so adding it to the home screen looks good.
- **Rich link previews.** Open Graph and Twitter tags with absolute URLs: title, one-line description, and a 1200×630 `og:image` (real screenshot plus the title works well), so the link unfurls nicely in Messages, Slack and social apps. Check the published page's tags and image respond before calling it done.

## External-facing prose

Text that someone other than Marcus will read goes through `naturally` for tone.

## Communicating decisions to Marcus

Present choices as trade-offs and consequences, not API trivia.

- **User and product impact first.** If something makes the experience better or worse, say what changes and how.
- **Name the real decision.** Which of maintainability, performance, flexibility, security, operability move, and in which direction.
- **Jargon last.** No leading with method names, file names, or pattern labels. Marcus decides on how the software is used and maintained; implementation detail follows only if needed.
- **Multi-aspect is normal.** One decision often touches several parts; map that briefly rather than collapsing to option A/B.
