---
name: agent-teams
description: Coordinate Claude Code agent teams for td-watch development. Use when creating teams, assigning tasks, running team sessions, or when any agent needs to understand team coordination rules. Covers roles, file ownership, friction protocol, quality gates, and common team configurations.
---

# Agent Teams for td-watch

## Roles

| Role | Agent file | Writes code | Key tools |
|------|-----------|-------------|-----------|
| Lead | (main session, delegate mode) | Never | Task management, SendMessage |
| Implementer | `.claude/agents/implementer.md` | Yes | Read, Write, Edit, Glob, Grep, Bash |
| Reviewer | `.claude/agents/reviewer.md` | No | Read, Glob, Grep, Bash |
| Researcher | `.claude/agents/researcher.md` | No | Read, Glob, Grep, Bash, WebFetch, WebSearch |
| Tester | `.claude/agents/tester.md` | Test files only | Read, Write, Edit, Glob, Grep, Bash |

**The lead never writes code.** Use delegate mode (Shift+Tab). Lead's job: break down work, assign tasks, triage friction, run quality gates, synthesize results.

## Hard Rules

1. **No two teammates edit the same file.** Split by file ownership. If two tasks touch the same file, make one depend on the other.
2. **Tasks are the coordination layer.** Task list is source of truth.
3. **Start small.** Lead + 2 teammates handles most work. Spawn more only when clearly beneficial.
4. **Never silently work around friction.** Fix small friction now. Report large friction to lead.
5. **Codify discoveries as skills.** If you searched for it, future agents will too.

## Common Configurations

### Lead + 2 Implementers (most common)
Split by file ownership. Example: one owns server routes, one owns page components.

### Lead + Researcher + Implementer
Researcher investigates first, implementer builds after findings arrive.

### Lead + 3 Implementers
For building multiple independent components/pages in parallel.

### Lead + Implementer + Reviewer
For security-sensitive or contract-critical code. Review loop after implementation.

## Task Guidelines

- Each task maps to clear file ownership boundaries
- 3-6 tasks per teammate per session
- Include acceptance criteria: "Build DataTable with sortable columns, pagination, loading/empty states, using design tokens" not just "Build DataTable"
- Use `blockedBy` when a task genuinely depends on another (page depends on server route). Don't use it for sequencing preference.

## Quality Gates

Run after implementation completes, before marking work done:

```bash
npx svelte-check          # type errors
npm run test:unit         # component tests
npm run test:server       # server route tests
npm run test:e2e          # integration tests
```

Lead can run these directly or assign to a tester teammate.

## Friction Protocol

Friction = any point where an agent can only proceed by guessing, bypassing, or working around.

1. **Surface immediately.** Never hide a workaround.
2. **Fix easy friction now** (< 10 min) — even before your main task.
3. **Task hard friction explicitly.** Create a real task, not a "later" note.
4. **Stop when blocked.** If progress requires human access/decisions, report and pause.

## Cross-Repository Work

- `~/code/td/` — td-sync server (Go)
- `~/code/td-watch/` — td-watch (SvelteKit)
- `~/code/sidecar/` — sidecar TUI (Go), reference only

Label which repo each task targets. Prefer separate tasks per repo. Researcher can explore `~/code/td/` while implementer works in `~/code/td-watch/`.

## Context Management

When the lead senses context pressure (many exchanges, approaching limits), write a summary task containing:
1. Team state — who's spawned, what each is working on
2. Task status — complete, in progress, blocked, why
3. Friction log — resolved and open
4. Key decisions made
5. Reference pointers to relevant docs
6. Next actions

## Key References

- `docs/agent-teams.md` — full team workflow documentation
- `docs/sync-admin-web-spec.md` — system spec, API contracts
- `docs/design-system.md` — design tokens, component specs
- `docs/agent-dev-guide.md` — dev environment, testing, logging

## Starting a Team Session

Tell Claude what to build and how to structure the team:

```
I'm working on [feature]. Create an agent team with delegate mode.
Spawn:
- [role] for [scope with file ownership]
- [role] for [scope with file ownership]
Break the work into tasks based on the spec. Assign clear file ownership.
```
