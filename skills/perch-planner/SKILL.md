---
name: perch-planner
description: Use the Perch plan CLI to create, read, update, and manage architectural plans. Covers project lifecycle, tree building, reviews, snapshots, facets, inputs, and export. Use when asked to retrieve a plan by name, build a plan tree, run a review, or interact with the planner in any way.
---

# Perch Planner CLI

The `plan` CLI is the primary interface for creating and managing architectural plans in Perch. Plans are hierarchical trees of nodes — areas, decisions, open questions, and future work — with built-in review, versioning, and export.

## Binary Location

The CLI lives at `agent-sidecar/.bin/plan` relative to the Perch repo root. If not on `$PATH`, use the full path or build it:

```bash
cd /path/to/perch && go build -o agent-sidecar/.bin/plan ./cmd/plan
```

## Quick Start

```bash
# Set up
plan new "My Project"
plan use "My Project"

# Build the tree
plan area add "Authentication"
plan add auth "Use OAuth2 with PKCE" --decision --rationale "Industry standard for SPAs"
plan add auth "Session storage strategy" --open
plan add auth "Token refresh mechanism" --future

# Read back
plan show auth
plan export
```

## Active Project

Most commands operate on the **active project**. Set it once per session:

```bash
plan use "Project Name"
```

The active project is stored in `~/.config/perch/plan-active-project`. Override with `PLAN_ACTIVE_PROJECT` env var.

## Retrieving a Plan by Name

```bash
# List all projects
plan list

# Show project details (ID, slug, revision, areas)
plan show-project "Project Name"

# Set as active and explore
plan use "Project Name"
plan show auth                    # Show a specific area/node
plan show auth/session-strategy   # Show nested node
plan export                       # Full plan as Markdown
plan export --depth 2             # Top 2 levels only
plan export --facet security      # Only security-tagged nodes
```

## Path System

Nodes are addressed by **slash-separated slugs**:

- `auth` — a root area named "Authentication" (slugified)
- `auth/session-strategy` — a child under auth
- `auth/session-strategy/oauth2` — deeper nesting

Slugs are auto-generated from node content: lowercase, alphanumeric + dashes, max 80 chars. Collisions among siblings get `-1`, `-2`, etc. appended automatically.

```bash
plan resolve auth/session-strategy   # Print the node's short ID (e.g., pn-a1b2c3d4)
```

## Short IDs

All entities use human-friendly short IDs with typed prefixes:

| Entity | Prefix | Example |
|--------|--------|---------|
| Node | `pn-` | `pn-a1b2c3d4` |
| Project | `pr-` | `pr-f0e1` |
| Review | `rv-` | `rv-abc123` |
| Input | `in-` | `in-d4e5` |
| Canvas | `cv-` | `cv-b2c3` |

All commands accept both short IDs and full UUIDs. Output always shows short IDs when available.

## Commands Reference

### Project Lifecycle

| Command | Description |
|---------|-------------|
| `plan new "Name"` | Create a project |
| `plan list` | List all projects |
| `plan show-project "Name"` | Show project details |
| `plan use "Name"` | Set active project |

### Tree Building

| Command | Description |
|---------|-------------|
| `plan area add "Area Name"` | Add a top-level area (root node) |
| `plan add <path> "content"` | Add a child node (default type: detail) |
| `plan add <path> "content" --decision --rationale "why"` | Add a decision node |
| `plan add <path> "content" --open` | Add an open question |
| `plan add <path> "content" --future` | Add future work |
| `plan show <path>` | Show node details and children |
| `plan show <path> --facet security` | Show filtered by facet |
| `plan show <path> --open` | Show only open questions |
| `plan resolve <path>` | Print node ID |
| `plan edit <path> "new content"` | Update node content |
| `plan edit --id <id> "new content"` | Update by ID (short ID or UUID) |
| `plan move <path> <new-parent-path>` | Move node to new parent |
| `plan status <path> <status>` | Set node status |
| `plan rm <path>` | Delete node (must have no children) |

### Node Types

- **detail** (default) — regular planning content
- **decision** — architectural/strategic choice, typically has a rationale
- **open_question** — unresolved question needing discussion
- **future** — speculative work, excluded from export by default

### Node Statuses

- **draft** (default) — in progress
- **accepted** — approved, ready for implementation
- **needs_review** — awaiting feedback
- **superseded** — replaced by another node

### Facets

Cross-cutting concern tags. Valid facets: `product`, `data`, `security`, `privacy`, `reliability`, `operability`, `cost`, `compliance`, `ux`.

```bash
plan tag auth/oauth2 --facet security
plan untag auth/oauth2 --facet security
```

### Inputs

Attach external context references to a project:

```bash
plan input add --type repository --name "perch" --uri "github.com/marcus/perch"
plan input add --type skill --name "sveltekit-latest" --description "Svelte 5 patterns"
plan input add --type document --name "RFC 7636" --uri "https://tools.ietf.org/html/rfc7636"
plan inputs                     # List all inputs
plan input rm <input-id>        # Remove an input
```

Valid input types: `repository`, `guideline`, `skill`, `document`, `api`, `design_system`.

### Reviews

Reviews let an agent (or human) propose changes to a subtree, then apply or reject them as a batch.

```bash
# Create a review scoped to a subtree
plan review start auth --lens security
plan review start auth --lens reliability --depth 2

# Agent adds proposals
plan review add-proposal <review-id> \
  --kind edit_node \
  --target auth/oauth2 \
  --content "Updated content" \
  --rationale "Clarify token rotation"

plan review add-proposal <review-id> \
  --kind add_child \
  --parent auth \
  --content "Rate limiting strategy" \
  --rationale "Missing from current plan"

plan review add-proposal <review-id> \
  --kind add_open_question \
  --parent auth \
  --content "Should we support SSO?"

plan review add-proposal <review-id> \
  --kind status_change \
  --target auth/session-strategy \
  --status accepted

# Complete the review
plan review complete <review-id> --summary "Added rate limiting, clarified OAuth"

# Show and apply
plan review show <review-id>
plan review apply <review-id>                        # Apply all proposals
plan review apply <review-id> --proposal <prop-id>   # Apply one
plan review reject <review-id>                       # Reject all
```

**Proposal kinds:** `edit_node`, `add_child`, `add_open_question`, `add_future`, `status_change`

**Stale detection:** Proposals become stale if the target node was modified or deleted since the review was created. Stale proposals are skipped during apply.

### Snapshots & Versioning

```bash
plan snapshot "Before refactor"       # Create immutable snapshot
plan diff <snapshot-id>               # Compare snapshot to current tree
```

### Export & Validation

```bash
plan export                           # Full Markdown export
plan export --depth 3                 # Limit depth
plan export --facet security          # Filter by facet
plan export --future true             # Include future nodes
plan validate                         # Check for structural issues
```

## Common Agent Workflows

### Retrieve and understand an existing plan

```bash
plan use "Project Name"
plan export                           # Get the full picture
plan show <area>                      # Drill into specific areas
plan show <area> --open               # Find open questions
```

### Build a plan from scratch

```bash
plan new "API Redesign"
plan use "API Redesign"

# Define areas
plan area add "Data Model"
plan area add "API Endpoints"
plan area add "Authentication"
plan area add "Migration Strategy"

# Add details, decisions, questions
plan add data-model "Use PostgreSQL with JSONB for flexible schemas" --decision \
  --rationale "Team already has PG expertise, JSONB handles evolving requirements"
plan add data-model "How to handle schema versioning?" --open
plan add api-endpoints "REST with OpenAPI spec" --decision
plan add migration-strategy "Zero-downtime migration plan" --future

# Tag with facets
plan tag data-model --facet data
plan tag authentication --facet security

# Add external references
plan input add --type repository --name "api-service" --uri "github.com/org/api"
plan input add --type document --name "Migration runbook" --uri "notion.so/..."
```

### Run a review pass

```bash
plan use "Project Name"
plan review start api-endpoints --lens security
# ... add proposals ...
plan review complete <id> --summary "Security review complete"
plan review apply <id>
```

### Snapshot before major changes

```bash
plan snapshot "Pre-review baseline"
# ... make changes ...
plan diff <snapshot-id>               # See what changed
```

## Database Location

Resolution order:
1. `PLAN_DB` environment variable
2. Perch config `DataDir + "/planner.db"`
3. Default: `~/.openclaw/workspace/data/planner.db`

## Optimistic Concurrency

Every node has a `revision` counter. Content edits require the current revision to match (enforced automatically by the CLI via read-then-write). The project itself has a `project_revision` that increments on every mutation, used for conflict detection in reviews.
