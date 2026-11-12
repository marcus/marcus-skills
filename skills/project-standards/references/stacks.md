# Go and JavaScript / TypeScript stacks

## Go stack

Match `tasks`, `td`, `sidecar`, `recall`, `comms`. Canonical reference is **`~/code/sidecar`**; `~/code/comms` is the leanest current copy of the same shape.

- `Makefile` with `build`, `install`, `install-local` (or equivalent) so the **local branch or worktree installs in one command**. Sidecar adds `install-worktree` and `use-homebrew` to switch between a dev build and the tap.
- **goreleaser v2** with a **Homebrew tap** target; `make release`, `release-dry-run`, `release-tap`.
- GitHub Actions: a CI workflow (`go-ci.yml` or `ci.yml`) plus `release.yml` triggered on `v*` tags, which verifies the tag against live `main` before publishing. Keep Actions aligned with how the repo actually releases.
- `go-version-file: go.mod` everywhere; toolchain via `mise`.

## JavaScript / TypeScript stack

- **The latest stable SvelteKit and Svelte, with TypeScript.**
- **SQLite** by default; **Postgres** when there's a real reason. Say what the reason was.
- UI: **Apple's glass aesthetic**, as close to a modern Mac app as the web allows. `~/code/clara-ui/DESIGN.md` is the reference, with `~/code/studio/DESIGN.md` as a second example.
