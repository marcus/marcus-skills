---
name: td-task-management
description: Task management for AI agents across context windows. Use when agents need to track work, log progress, hand off state, and maintain context across sessions. Includes workflows for single-issue focus, multi-issue work sessions, and structured handoffs. Essential for AI-assisted development where context windows reset between sessions.
---

# td - Task Management for AI Agents

## Overview

`td` is a minimalist CLI for tracking tasks and maintaining agent memory across context windows. When your AI session ends, `td` captures what was done, what remains, and what decisions were made—so the next session picks up exactly where the last one left off.

**Core capability:** Run `td usage` and get everything needed for the next action—current focus, pending reviews, open issues, recent decisions.

## Quick Start

### Session Start (Every Time)

```bash
td usage --new-session  # Auto-rotation + see current state
```

Output tells you:
- Active work sessions and recent decisions
- What issues are pending review (you can review these)
- Highest priority open issues
- Recent handoffs from previous sessions

### Single-Issue Workflow

For focused work on one issue:

```bash
td start <issue-id>                    # Begin work
td log "OAuth callback implemented"    # Track progress
td log --decision "Using JWT tokens"   # Log decisions
td handoff <id> --done "..." --remaining "..."  # Capture state
td review <id>                         # Submit for review
```

### Multi-Issue Workflow (Recommended for Agents)

For agents handling related issues:

```bash
td ws start "Auth implementation"      # Start work session
td ws tag td-a1b2 td-c3d4             # Associate issues
td ws log "Shared token storage"       # Log to all tagged issues
td ws handoff                          # Capture state, end session
```

## Key Workflows

### Workflow 1: Starting New Work

```bash
# 1. Check what to work on
td usage          # See current state
td next           # Highest priority open issue
td critical-path  # What unblocks most work

# 2. Start work
td start <id>

# 3. Begin logging
td log "Started implementation"
```

### Workflow 2: Handing Off Work

This is **critical** for agent-to-agent handoffs:

```bash
td handoff <id> \
  --done "OAuth flow, token storage" \
  --remaining "Refresh token rotation, error handling" \
  --decision "Using JWT for stateless auth" \
  --uncertain "Should tokens expire on password change?"
```

Keys:
- `--done` - What's actually complete (be honest)
- `--remaining` - What's left (be specific)
- `--decision` - Why you chose approach X
- `--uncertain` - What you're unsure about

Next session will see all this context with `td usage` or `td context <id>`.

### Workflow 3: Reviewing Code

```bash
# 1. See reviewable issues
td reviewable

# 2. Check details
td show <id>
td context <id>

# 3. Approve or reject
td approve <id> --reason "Reviewed diff, looks good"
# If a sub-agent reviewed work you implemented:
td approve <id> --reviewed-by "code-reviewer sub-agent"
# If you implemented it and reviewed it yourself (trusted mode):
td approve <id> --self-review --reason "Reviewed own diff, tests pass"
# Or reject:
td reject <id> --reason "Missing error handling"
```

**Note (trusted mode):** The default `review_policy_mode` is `trusted`. Independent review is preferred — a session that did not implement the issue approves it with `td approve <id> --reason "..."`. When you implemented it, the flags exist so the record matches reality, and you pick by who actually reviewed:

- **a sub-agent with its own `TD_CONTEXT_ID`** — best; let it approve or `--record-only`, so the independence is mechanically verified
- **a sub-agent sharing your session** — `td approve <id> --reviewed-by "<who>"`; no `--reason` needed, the name is the substance
- **nobody but you** — `td approve <id> --self-review --reason "..."`, which stamps the audit row

Naming a reviewer who did not review is worse than an honest `--self-review`: it reads as independent in the audit trail.

### Workflow 4: Handling Blockers

```bash
# 1. Log the blocker
td log --blocker "Waiting on API spec from backend team"

# 2. Work on something else
td next              # Get another issue
td ws tag td-e5f6   # Add to work session

# 3. Come back to blocked issue later
td context td-a1b2  # Refresh context when blocker resolves
```

## Commands by Category

### Checking Status
- `td usage` - Current state, reviews, next steps
- `td usage -q` - Compact view (after first read)
- `td current` - What you're working on
- `td ws current` - Current work session state
- `td next` - Highest priority open
- `td critical-path` - What unblocks most work

### Working on Issues
- `td start <id>` - Begin work
- `td log "msg"` - Track progress
- `td log --decision "..."` - Log decision
- `td log --blocker "..."` - Log blocker
- `td show <id>` - View details
- `td context <id>` - Full context for resuming

### Handing Off
- `td handoff <id> --done "..." --remaining "..."` - Single issue
- `td ws handoff` - Multi-issue work session

### Reviews
- `td review <id>` - Submit for review
- `td reviewable` - Issues you can review
- `td approve <id> --reason "..."` - Approve (independent session preferred)
- `td approve <id> --reviewed-by "<who>"` - Approve work you implemented that someone else reviewed
- `td approve <id> --record-only --reason "..."` - Record a review without closing (reviewer sub-agent)
- `td approve <id> --self-review --reason "..."` - Approve own work (trusted mode; audited)
- `td reject <id> --reason "..."` - Reject

### Creating/Managing Issues
- `td create "title" --type feature --priority P1` - Create
- `td list` - List all
- `td list --status in_progress` - Filter by status
- `td block <id>` - Mark as blocked
- `td delete <id>` - Delete

### File Tracking
- `td link <id> <files...>` - Track files with issue
- `td files <id>` - Show file changes

### Other
- `td monitor` - Live dashboard
- `td session --new "name"` - Force new session
- `td undo` - Undo last action

See [quick_reference.md](references/quick_reference.md) for full command listing.

## Resources

### [quick_reference.md](references/quick_reference.md)
Complete command reference organized by task type.

### [ai_agent_workflows.md](references/ai_agent_workflows.md)
Detailed workflows for common AI agent scenarios:
- Single-issue focus
- Multi-issue work sessions
- Handling blockers
- Resuming work
- Code review process
- Tips for AI agents

## Issue Lifecycle

```
open → in_progress → in_review → closed
         |              |
         v              | (reject)
     blocked -----------+
```

## Key Principles

**Session Isolation:** Every terminal/context gets a unique session ID, so give each sub-agent its own `TD_CONTEXT_ID` — that is what turns "a sub-agent reviewed it" from an assertion into something td can verify. In the default `trusted` mode, a session that implemented an issue should have an independent session review it. When the reviewer shares your session, `--reviewed-by "<who>"` records who actually reviewed; when nobody else looked, `--self-review --reason "..."` stamps `self_review=true` on the review row. Independent review is still the norm; the other two are disclosures, not default paths.

**Structured Handoffs:** Don't just say "here's what I did"—structure it with done/remaining/decisions/uncertain so next agent has clear context.

**Minimal:** Does one thing. Single binary, SQLite local storage (`.todos/`), no server, works with any AI tool.

## For AI Agents

Always start conversation with:
```bash
td usage --new-session
```

This auto-rotates sessions and gives you current state. Then:

1. **Single focused issue** → Use single-issue workflow
2. **Multiple related issues** → Use `td ws start` for work sessions
3. **Before context ends** → Always `td handoff` or `td ws handoff`
4. **Log decisions** → Use `--decision` flag to explain reasoning
5. **Log uncertainty** → Use `--uncertain` flag to mark unknowns
6. **Track files** → Use `td link` so future sessions know what changed

See [ai_agent_workflows.md](references/ai_agent_workflows.md) for detailed examples.
