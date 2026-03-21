---
name: td-ralph-loop
description: Set up and run autonomous overnight coding loops that process td epic tasks one at a time. Includes the loop runner, live tail monitor, and prompt template. Use when automating multi-day feature development across many tasks with td for state management.
---

# TD Ralph Loop

Autonomous coding loop that processes td epic tasks one at a time, with built-in resilience for rate limits, stuck iterations, and credit exhaustion. Named after Ralph Wiggum ("I'm in danger!") because it keeps going no matter what.

## When to use

- You have a td epic with 10-100+ tasks and want to run them autonomously
- Multi-day/overnight feature development
- Bulk implementation where each task is independent enough for one agent iteration

## Quick Start

1. Create your epic and tasks in td (manually or with the setup script)
2. Write a project-specific prompt file
3. Run the loop: `./scripts/ralph.sh <epic-id>`
4. Monitor: `./scripts/ralph-tail.sh <epic-id>`

## Architecture

```
ralph.sh (loop runner)
  ├── Reads prompt from ralph-prompt.md
  ├── Runs `claude -p` for each iteration
  ├── Handles failures with exponential backoff
  ├── Detects rate limits vs real failures
  ├── 70-minute timeout per iteration
  └── Logs to ralph-logs/

ralph-tail.sh (live monitor)
  ├── Shows epic progress (done/in-progress/open)
  ├── Shows current task
  ├── Tails latest iteration log
  └── Auto-switches when new iteration starts

ralph-prompt.md (agent instructions)
  ├── Step 0: Review tasks in review (close to unblock deps)
  ├── Step 1: Read td state, pick highest priority unblocked task
  ├── Step 2: Assess task type (story → decompose, task → implement)
  ├── Step 3: Implement with quality gates
  ├── Step 4: Verify (browser screenshots or tests)
  ├── Step 5: Commit and close
  └── Step 6: Exit (one task per iteration)
```

## Scripts

### ralph.sh — Loop Runner

Copy this to your project's `scripts/` directory and adjust `REPO_DIR`.

```bash
#!/bin/bash
# Ralph Loop — autonomous coding loop
# Uses TD for state, resilient to credit exhaustion
#
# Usage:
#   ./scripts/ralph.sh <epic-id>
#   ./scripts/ralph.sh <epic-id> --model sonnet
#   ./scripts/ralph.sh <epic-id> --max-budget 5
#   ./scripts/ralph.sh <epic-id> --dry-run
#   ./scripts/ralph.sh <epic-id> --timeout 3600

set -uo pipefail

EPIC_ID="${1:?Usage: ./scripts/ralph.sh <epic-id> [--model MODEL] [--max-budget USD] [--dry-run] [--timeout SECS]}"
shift

# Defaults
MODEL="opus"
FALLBACK_MODEL="sonnet"
MAX_BUDGET=""
DRY_RUN=false
MAX_CONSECUTIVE_FAILURES=10
MAX_BACKOFF=1800  # 30 min cap
PAUSE_BETWEEN=5   # seconds between successful iterations
ITER_TIMEOUT=4200 # 70 minutes per iteration

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        --model) MODEL="$2"; shift 2 ;;
        --fallback) FALLBACK_MODEL="$2"; shift 2 ;;
        --max-budget) MAX_BUDGET="$2"; shift 2 ;;
        --dry-run) DRY_RUN=true; shift ;;
        --pause) PAUSE_BETWEEN="$2"; shift 2 ;;
        --timeout) ITER_TIMEOUT="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

REPO_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/ralph-logs"
PROMPT_FILE="$SCRIPT_DIR/ralph-prompt.md"

BACKOFF=30
ITERATION=0
CONSECUTIVE_FAILURES=0

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/ralph.log"
}

count_open_tasks() {
    cd "$REPO_DIR" && td list --epic "$EPIC_ID" -s open,in_progress 2>/dev/null | grep -c "td-" || echo "0"
}

has_open_tasks() {
    local count
    count=$(count_open_tasks)
    [[ "$count" -gt 0 ]]
}

is_credit_error() {
    local logfile="$1"
    grep -qi \
        -e "rate.limit" \
        -e "rate_limit_error" \
        -e "overloaded" \
        -e "insufficient.*credit" \
        -e "billing" \
        -e "quota" \
        -e "capacity" \
        -e "too many requests" \
        -e "529" \
        -e "ResourceExhausted" \
        "$logfile" 2>/dev/null
}

# Validate inputs
if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: Prompt file not found at $PROMPT_FILE"
    echo "Create scripts/ralph-prompt.md with your project-specific agent instructions."
    exit 1
fi

if ! cd "$REPO_DIR" && td show "$EPIC_ID" >/dev/null 2>&1; then
    echo "Warning: Could not verify epic $EPIC_ID exists in td"
fi

log "============================================"
log "Ralph Loop starting"
log "  Epic:     $EPIC_ID"
log "  Model:    $MODEL (fallback: $FALLBACK_MODEL)"
log "  Repo:     $REPO_DIR"
log "  Timeout:  ${ITER_TIMEOUT}s per iteration"
log "  Max budget/iter: ${MAX_BUDGET:-unlimited}"
log "============================================"

while has_open_tasks; do
    ITERATION=$((ITERATION + 1))
    REMAINING=$(count_open_tasks)

    log ""
    log "=== Iteration $ITERATION === ($REMAINING tasks remaining)"

    if $DRY_RUN; then
        log "[DRY RUN] Would run: claude -p <prompt> --model $MODEL --epic $EPIC_ID"
        cd "$REPO_DIR" && td list --epic "$EPIC_ID" -s open,in_progress 2>/dev/null | head -5
        break
    fi

    ITER_LOG="$LOG_DIR/iter-$(printf '%04d' $ITERATION)-$(date '+%Y%m%d-%H%M%S').log"

    # Build claude command
    CLAUDE_ARGS=(
        -p "$(cat "$PROMPT_FILE")"
        --model "$MODEL"
        --fallback-model "$FALLBACK_MODEL"
        --dangerously-skip-permissions
        --append-system-prompt "EPIC_ID=$EPIC_ID. You are in iteration $ITERATION. There are $REMAINING open tasks remaining."
        --name "ralph-$(printf '%04d' $ITERATION)"
    )

    [[ -n "$MAX_BUDGET" ]] && CLAUDE_ARGS+=(--max-budget-usd "$MAX_BUDGET")

    log "  Running claude... (log: $(basename "$ITER_LOG"))"

    # Use `script` for unbuffered output, `timeout` to prevent stuck iterations
    if (cd "$REPO_DIR" && timeout "$ITER_TIMEOUT" script -q "$ITER_LOG" claude "${CLAUDE_ARGS[@]}" >/dev/null 2>&1); then
        log "  Iteration $ITERATION completed successfully"
        BACKOFF=30
        CONSECUTIVE_FAILURES=0
        sleep "$PAUSE_BETWEEN"
    else
        EXIT_CODE=$?
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))

        if [[ $CONSECUTIVE_FAILURES -ge $MAX_CONSECUTIVE_FAILURES ]]; then
            log "  FATAL: $MAX_CONSECUTIVE_FAILURES consecutive failures. Stopping."
            log "  Last log: $ITER_LOG"
            exit 1
        fi

        if is_credit_error "$ITER_LOG"; then
            log "  Credit/rate limit hit (attempt $CONSECUTIVE_FAILURES/$MAX_CONSECUTIVE_FAILURES)"
            log "  Backing off ${BACKOFF}s..."
            sleep "$BACKOFF"
            BACKOFF=$((BACKOFF * 2))
            [[ $BACKOFF -gt $MAX_BACKOFF ]] && BACKOFF=$MAX_BACKOFF
        else
            log "  Failed with exit code $EXIT_CODE (attempt $CONSECUTIVE_FAILURES/$MAX_CONSECUTIVE_FAILURES)"
            log "  Last 3 lines of output:"
            tail -3 "$ITER_LOG" 2>/dev/null | while IFS= read -r line; do
                log "    $line"
            done
            sleep 10
        fi
    fi
done

log ""
log "============================================"
log "Ralph Loop complete!"
log "  Total iterations: $ITERATION"
log "  Epic: $EPIC_ID"
log "============================================"
```

### ralph-tail.sh — Live Monitor

```bash
#!/bin/bash
# Ralph Loop — live tail with status
# Usage: ./scripts/ralph-tail.sh <epic-id>

LOG_DIR="$(cd "$(dirname "$0")" && pwd)/ralph-logs"
EPIC_ID="${1:?Usage: ./scripts/ralph-tail.sh <epic-id>}"

if [[ ! -d "$LOG_DIR" ]]; then
    echo "No log directory found at $LOG_DIR"
    exit 1
fi

DIM='\033[2m'
BOLD='\033[1m'
GREEN='\033[32m'
YELLOW='\033[33m'
CYAN='\033[36m'
RED='\033[31m'
RESET='\033[0m'

show_status() {
    clear
    echo -e "${BOLD}Ralph Loop — Live Tail${RESET}"
    echo ""

    local total=$(td list --epic "$EPIC_ID" 2>/dev/null | grep -c "td-" | tr -d '[:space:]' || echo "0")
    local done=$(td list --epic "$EPIC_ID" -s closed,in_review 2>/dev/null | grep -c "td-" | tr -d '[:space:]' || echo "0")
    local review=$(td list --epic "$EPIC_ID" -s in_review 2>/dev/null | grep -c "td-" | tr -d '[:space:]' || echo "0")
    local open=$(td list --epic "$EPIC_ID" -s open 2>/dev/null | grep -c "td-" | tr -d '[:space:]' || echo "0")
    local in_prog=$(td list --epic "$EPIC_ID" -s in_progress 2>/dev/null | grep -c "td-" | tr -d '[:space:]' || echo "0")

    echo -e "  ${CYAN}Epic:${RESET} $EPIC_ID    ${GREEN}Done: $done${RESET} ${DIM}(${review} in review)${RESET}  ${YELLOW}In Progress: $in_prog${RESET}  ${DIM}Open: $open${RESET}  ${DIM}Total: $total${RESET}"

    if [[ "$in_prog" -gt 0 ]]; then
        local current=$(td list --epic "$EPIC_ID" -s in_progress 2>/dev/null | head -1)
        echo -e "  ${YELLOW}Working on:${RESET} $current"
    fi

    local latest=$(ls -t "$LOG_DIR"/iter-*.log 2>/dev/null | head -1)
    if [[ -n "$latest" ]]; then
        local iter_name=$(basename "$latest" .log)
        local line_count=$(wc -l < "$latest" 2>/dev/null | tr -d ' ')
        echo -e "  ${DIM}Log: $iter_name ($line_count lines)${RESET}"
    fi

    local completed=$(grep "completed successfully" "$LOG_DIR/ralph.log" 2>/dev/null | tail -3)
    if [[ -n "$completed" ]]; then
        echo ""
        echo -e "  ${GREEN}Recent completions:${RESET}"
        echo "$completed" | while IFS= read -r line; do
            echo -e "    ${DIM}$line${RESET}"
        done
    fi

    local failures=$(grep -E "Failed|Credit|FATAL" "$LOG_DIR/ralph.log" 2>/dev/null | tail -2)
    if [[ -n "$failures" ]]; then
        echo ""
        echo -e "  ${RED}Recent issues:${RESET}"
        echo "$failures" | while IFS= read -r line; do
            echo -e "    ${RED}$line${RESET}"
        done
    fi

    echo ""
    echo -e "${DIM}──────────────────────────────────────────────────────${RESET}"
    echo ""
}

show_status

while true; do
    LATEST=$(ls -t "$LOG_DIR"/iter-*.log 2>/dev/null | head -1)

    if [[ -z "$LATEST" ]]; then
        echo -e "${DIM}Waiting for first iteration log...${RESET}"
        sleep 2
        continue
    fi

    tail -f "$LATEST" &
    TAIL_PID=$!

    while true; do
        sleep 3
        NEW_LATEST=$(ls -t "$LOG_DIR"/iter-*.log 2>/dev/null | head -1)
        if [[ "$NEW_LATEST" != "$LATEST" ]]; then
            kill $TAIL_PID 2>/dev/null
            wait $TAIL_PID 2>/dev/null
            echo ""
            show_status
            break
        fi
    done
done
```

## Prompt Template

Create `scripts/ralph-prompt.md` for your project. Below is the generic template — customize the project-specific sections.

```markdown
You are working inside the Ralph Loop — an autonomous coding loop that processes
tasks one at a time.

The epic ID and iteration number are provided in your system prompt as EPIC_ID=<value>.

## Quality bar

Every feature you implement should be:

- **Complete**: All edge cases handled. Proper error states.
- **Polished**: No rough edges. Professional feel.
- **Deep**: Don't implement the happy path and call it done.

Do NOT take shortcuts to save tokens. We are optimizing for quality, not speed.

## What to do this iteration

### Step 0: Review tasks in review

**Before picking up new work, always check for tasks awaiting review:**

td list --epic $EPIC_ID -s in_review --long

If there are tasks in `in_review`, review them **one at a time** before moving
to new work. For each task:

1. Read the task description and session log: `td show <id>`
2. Check the git diff for the implementation
3. Verify the code follows project conventions and quality standards
4. **If good:** `td close <id>` to unblock dependent tasks
5. **If issues:**
   - Small fixes: fix them yourself, commit, then `td close <id>`
   - Large issues: create a new task in the epic, then `td close <id>`
6. Log your review: `td log <id> "Reviewed: <summary>"`

**Review at most 3 tasks per iteration.**

### Step 1: Read TD state

td list --epic $EPIC_ID -s open,in_progress --long

If any task is `in_progress`, resume it first — check `td context <id>` for
prior state. Otherwise pick the first `open` task by priority.

### Step 2: Assess the task type

**If it's a story (high-level feature area) with no subtasks:**

- Explore the existing codebase to understand what's already built
- Decompose into concrete, implementable subtasks
- Set dependencies between subtasks where order matters
- Log completion and exit — the loop will call you again

**If it's an implementable task:** Continue to Step 3.

### Step 3: Implement

td start <id>

1. Check what exists — don't rebuild what's already built
2. Write the code following project conventions
3. Build the **complete feature**, not just the skeleton
4. Write tests where the feature is testable
5. Run quality gates (linting, type checking, build)

### Step 4: Verify it works

**Before marking any task complete, you MUST prove it works.**

- Run the test suite
- If UI changes: capture browser screenshots as proof
- Log verification: `td log <id> "Verified: <what you proved>"`
- If verification reveals issues, fix them before proceeding

### Step 5: Commit and close

Only after verification passes:

1. Commit: `git commit -m "feat: <summary> (td-<id>)"`
2. Close: `td close <id>`

### Step 6: Exit

After completing ONE task, exit cleanly. The loop will call you again.

## Rules

- **ONE task per iteration.** Complete it, verify it, commit it, close it, exit.
- **TD is your source of truth.** Read it fresh every iteration.
- **Quality gates before every commit.**
- **Prove it works.** No exceptions.
- **Build complete features.** Not skeletons.
- **If stuck, log and skip.** `td log <id> "Blocked: <reason>"` then `td block <id>`.
- **Keep subtasks small but complete.** Tightly scoped but fully implemented.
- **Commit messages reference td.** Format: `feat|fix|chore: <summary> (td-<id>)`
```

## Learnings & Best Practices

These come from running the loop for 60+ iterations on a real project:

### Loop Management

- **70-minute timeout is essential.** Without it, stuck iterations can block the loop for 8+ hours. The agent sometimes hangs waiting on an API response or enters a retry loop.
- **`script -q` for unbuffered output.** Without it, `claude -p` buffers stdout when piped to a file, so the tail monitor shows 0 lines until the iteration completes.
- **Kill stuck iterations freely.** Exit code 143 (SIGTERM) is handled gracefully — the loop logs the failure and moves on. The task stays `open` or `in_progress` and gets retried.
- **Exponential backoff for rate limits.** Starts at 30s, doubles to max 30min. Resets on success.

### Task Design

- **Tasks must be completable in one iteration.** If a task takes more than 60 minutes, it's too big. Break it down.
- **Dependencies prevent wasted work.** Wire dependencies between tasks so the loop doesn't try to build a UI for an API that doesn't exist yet.
- **P0 for blocking bugs, P1 for core features, P2 for everything else.** The loop picks by priority, so urgent fixes get done first.
- **Agents use `td review` not `td close`.** This is fine — but if nothing reviews them, dependent tasks stay blocked forever. Step 0 (review before new work) fixes this by having each iteration review up to 3 pending tasks.

### Prompt Design

- **Be explicit about quality.** Agents will take the shortest path unless you tell them not to. "Do NOT take shortcuts to save tokens" is necessary.
- **Require proof.** Without the verification step, agents will claim something works without testing it.
- **Include project-specific context.** Reference skills, conventions, and existing code patterns so agents don't reinvent the wheel.
- **Reference the project's CLAUDE.md.** Agents should follow the same rules as interactive sessions.

### Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| 0 lines in tail monitor | stdout buffering | Use `script -q` wrapper (in the template) |
| Iteration runs for hours | Agent stuck on API/retry | Add timeout (in the template) |
| 22 tasks "in review" blocking everything | Agents don't close tasks | Add Step 0 review phase (in the template) |
| Agent rebuilds existing code | No codebase exploration step | Add "check what exists" instruction |
| Task works in dev, breaks in prod | No verification step | Require browser screenshots or test runs |
| Agent creates duplicate code | No awareness of sibling modules | Add "reuse from X module" section |
| Epic stalls with 0 unblocked tasks | All tasks blocked by unreviewed deps | Step 0 clears the review queue |

### Monitoring

The tail script shows real-time progress. For deeper monitoring:

```bash
# Check what's in each status
td list --epic <id> -s in_review    # Blocked until reviewed
td list --epic <id> -s open         # Available to pick up
td list --epic <id> -s in_progress  # Currently being worked on

# See what the current iteration is doing
tail -f scripts/ralph-logs/iter-*.log | tail -1  # Latest log

# Kill a stuck iteration (loop recovers automatically)
kill <pid>

# Check git progress
git log --oneline --since="8 hours ago"
```

## Setup from Scratch

For a new project:

1. Create the epic: `td epic create "My Feature"`
2. Create tasks under it with priorities and dependencies
3. Copy the scripts to `scripts/ralph.sh`, `scripts/ralph-tail.sh`
4. Write `scripts/ralph-prompt.md` customized for your project
5. Run: `./scripts/ralph.sh <epic-id>`
6. Monitor: `./scripts/ralph-tail.sh <epic-id>`

Optional: use a setup script (like `ralph-setup.sh`) that reads a plan/spec and creates tasks automatically with Claude.
