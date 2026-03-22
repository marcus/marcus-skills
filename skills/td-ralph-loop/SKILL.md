---
name: td-ralph-loop
description: Set up and run autonomous overnight coding loops that process td epic tasks one at a time. Includes the loop runner, Rich TUI cockpit dashboard, and prompt template. Use when automating multi-day feature development across many tasks with td for state management.
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
4. Monitor: `./scripts/ralph-tail.py <epic-id>`

## Architecture

```
ralph.sh (loop runner)
  ├── Reads prompt from ralph-prompt.md
  ├── Runs `claude -p` for each iteration
  ├── Handles failures with exponential backoff
  ├── Detects rate limits vs real failures
  ├── Configurable timeout per iteration (default 45min)
  └── Logs to ralph-logs/

ralph-tail.py (Rich TUI cockpit dashboard)
  ├── Flicker-free ~2fps rendering via Rich Live display
  ├── Gauges: task counts, iterations, commits/24h, lines changed, heartbeat
  ├── Commits: last 8 with per-commit +ins -del (files) stats
  ├── Velocity: bar chart of commit rate across 1h/6h/24h windows
  ├── Loop: iteration count, current log, completions/failures
  ├── Tasks: in-progress highlighted, recent activity by status
  ├── Up Next: next 3 open tasks by priority the loop will pick up
  ├── Log viewer: scrollable (j/k/g/G/d/u), falls back to previous if current empty
  ├── Heartbeat: LAST ACTIVITY timer (green <2m, amber <10m, red >10m)
  └── Keyboard: q=quit, j/k=scroll, g/G=top/bottom, d/u=half-page

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
ITER_TIMEOUT=2700 # 45 minutes per iteration

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
    (cd "$REPO_DIR" && td list --epic "$EPIC_ID" -s open,in_progress,in_review 2>/dev/null | grep -c "td-") || echo "0"
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

if ! (cd "$REPO_DIR" && td show "$EPIC_ID" >/dev/null 2>&1); then
    echo "Warning: Could not verify epic $EPIC_ID exists in td"
fi

cleanup() {
    log "  Stopped by signal (PID $$)"
    exit 130
}
trap cleanup SIGINT SIGTERM

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

    # timeout prevents stuck iterations; simple redirect for log capture
    if (cd "$REPO_DIR" && timeout "$ITER_TIMEOUT" claude "${CLAUDE_ARGS[@]}" > "$ITER_LOG" 2>&1); then
        log "  Iteration $ITERATION completed successfully"
        BACKOFF=30
        CONSECUTIVE_FAILURES=0
        sleep "$PAUSE_BETWEEN"
    else
        EXIT_CODE=$?

        if [[ $EXIT_CODE -eq 124 ]]; then
            # timeout(1) returns 124 — not a real failure, just a slow iteration
            log "  Iteration $ITERATION timed out — agent was likely slow, not broken"
            BACKOFF=30
            sleep "$PAUSE_BETWEEN"
            continue
        fi

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

### ralph-tail.py — Rich TUI Cockpit Dashboard

Full-screen Rich TUI dashboard with flicker-free rendering, scrollable log viewer, and keyboard navigation. Requires `pip install rich`.

```
┌─────────────────────────────────────────────────────────────┐
│ RALPH LOOP  <epic-id>  08:15:32    q=quit j/k=scroll g/G=… │
├─────────────── gauges ──────────────────────────────────────┤
│ CLOSED  REVIEW  ACTIVE  OPEN  ITERS  COMMITS/24h  LINES  … │
│   12       5       1      8    31       55       +2.1k -340 │
├──── commits ──────────────┬──── velocity ───────────────────┤
│ 02b50ca  fix: text...     │  1h ████░░░░░ 3 (3.0/h)        │
│ 10a76ea  feat: drag...    │  6h ███████░░ 18 (3.0/h)       │
│ ...                       │ 24h █████████ 55 (2.3/h)       │
│                           ├──── loop ───────────────────────┤
│                           │ iterations: 31  current: iter…  │
│                           │ last write: 2m ago              │
├──── log (scrollable) ─────┬─────────── tasks ───────────────┤
│ Task complete. Here's...  │ ACTIVE  td-9dd067: Text drag… │
│ **Reviews completed (3)** │ REVIEW  td-e37d05: Text dese… │
│ ...                       │ CLOSED  td-22503c: Property…  │
│                           ├─────────── up next ─────────────┤
│                           │ P1  td-0469cf: Canvas design… │
│                           │ P1  td-32b165: Text stroke …  │
│                           │ P2  td-e31ac7: Design token…  │
└───────────────────────────┴─────────────────────────────────┘
```

Copy `scripts/ralph-tail.py` from below. Install dependency: `pip install rich`.

```python
#!/usr/bin/env python3
"""Ralph Loop — cockpit dashboard.

Live-updating dashboard showing epic progress, commit velocity, lines changed,
iteration status, and scrollable log viewer. Uses Rich for flicker-free rendering.

Usage:
    ./scripts/ralph-tail.py <epic-id>
    ./scripts/ralph-tail.py <epic-id>

Keys: q = quit, j/k or up/down = scroll log, g/G = top/bottom

Requires: pip install rich
"""

import os
import re
import subprocess
import sys
import tty
import termios
import time
import threading
import signal
from pathlib import Path
from datetime import datetime

from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# ── Config ──────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_DIR = SCRIPT_DIR / "ralph-logs"
STATUS_REFRESH = 10  # seconds between td/git data refresh

# ── Helpers ─────────────────────────────────────────────────────────────────


def run(cmd: str, cwd: str | None = None) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15,
            cwd=cwd or str(SCRIPT_DIR.parent),
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return ""


def count_tasks(epic_id: str, status: str) -> int:
    out = run(f"td list --epic {epic_id} -s {status} 2>/dev/null")
    return len(re.findall(r"td-[a-f0-9]+", out))


def get_in_progress(epic_id: str) -> list[str]:
    out = run(f"td list --epic {epic_id} -s in_progress 2>/dev/null")
    return [l.strip() for l in out.splitlines() if l.strip()]


def get_recent_commits(n: int = 8) -> list[dict]:
    """Get recent commits with lines changed stats."""
    out = run(f"git log --oneline --format='%h|%ar|%s' --shortstat -{n}")
    commits = []
    lines = out.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        parts = line.split("|", 2)
        if len(parts) == 3:
            commit = {"hash": parts[0], "ago": parts[1], "msg": parts[2], "stat": ""}
            # --shortstat puts a blank line then the stat line after each commit
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and "changed" in lines[j]:
                commit["stat"] = _parse_shortstat(lines[j])
                i = j
            commits.append(commit)
        i += 1
    return commits


def _parse_shortstat(line: str) -> str:
    """Turn '3 files changed, 148 insertions(+), 12 deletions(-)' into '+148 -12 3f'."""
    files = ins = dels = 0
    m = re.search(r"(\d+) file", line)
    if m:
        files = int(m.group(1))
    m = re.search(r"(\d+) insertion", line)
    if m:
        ins = int(m.group(1))
    m = re.search(r"(\d+) deletion", line)
    if m:
        dels = int(m.group(1))
    parts = []
    if ins:
        parts.append(f"+{ins}")
    if dels:
        parts.append(f"-{dels}")
    if files:
        parts.append(f"{files}f")
    return " ".join(parts)


def get_commit_velocity() -> dict:
    """Calculate commit rates over different windows."""
    last_1h = int(run("git log --since='1 hour ago' --oneline | wc -l").strip() or "0")
    last_6h = int(run("git log --since='6 hours ago' --oneline | wc -l").strip() or "0")
    last_24h = int(run("git log --since='24 hours ago' --oneline | wc -l").strip() or "0")

    stat_out = run("git diff --shortstat HEAD~50 HEAD 2>/dev/null")
    total_ins = total_dels = 0
    m = re.search(r"(\d+) insertion", stat_out)
    if m:
        total_ins = int(m.group(1))
    m = re.search(r"(\d+) deletion", stat_out)
    if m:
        total_dels = int(m.group(1))

    now = time.time()
    last_ts = run("git log --format='%ct' -1")
    commit_delta = None
    since_last = ""
    if last_ts:
        commit_delta = now - int(last_ts)
        if commit_delta < 60:
            since_last = f"{int(commit_delta)}s ago"
        elif commit_delta < 3600:
            since_last = f"{int(commit_delta / 60)}m ago"
        else:
            since_last = f"{int(commit_delta / 3600)}h {int((commit_delta % 3600) / 60)}m ago"

    # Heartbeat: absolute timestamp of most recent activity (commit or log write)
    latest_activity_ts = int(last_ts) if last_ts else 0
    latest_log = sorted(LOG_DIR.glob("iter-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    if latest_log:
        log_mtime = latest_log[0].stat().st_mtime
        latest_activity_ts = max(latest_activity_ts, log_mtime)

    return {
        "1h": last_1h, "6h": last_6h, "24h": last_24h,
        "ins": total_ins, "dels": total_dels,
        "last": since_last,
        "heartbeat_ts": latest_activity_ts,
    }


def get_next_open_tasks(epic_id: str, n: int = 3) -> list[dict]:
    """Get the next N open tasks by priority (what the loop will pick up next)."""
    out = run(f"td list --epic {epic_id} -s open 2>/dev/null")
    tasks = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        # Format: td-XXXXXX  [P1]  Title  type  [open]
        m = re.match(r"(td-[a-f0-9]+)\s+\[([^\]]+)\]\s+(.+?)\s+(feature|bug|task|story)\s+\[open\]", line)
        if m:
            tasks.append({
                "id": m.group(1),
                "priority": m.group(2),
                "title": m.group(3).strip(),
                "type": m.group(4),
            })
            if len(tasks) >= n:
                break
    return tasks


def get_recent_td_activity(epic_id: str, n: int = 6) -> list[dict]:
    """Get recent task activity from git commit references."""
    git_out = run("git log --oneline --format='%h %s' -25")
    seen = set()
    activities = []
    for line in git_out.splitlines():
        match = re.search(r"\(td-([a-f0-9]+)\)", line)
        if match:
            task_id = f"td-{match.group(1)}"
            if task_id in seen:
                continue
            seen.add(task_id)
            task_out = run(f"td show {task_id} 2>/dev/null")
            title_match = re.match(r"td-[a-f0-9]+: (.+)", task_out)
            title = title_match.group(1) if title_match else task_id
            status_match = re.search(r"Status: \[(\w+)\]", task_out)
            status = status_match.group(1) if status_match else "?"
            activities.append({"id": task_id, "title": title, "status": status})
            if len(activities) >= n:
                break
    return activities


def get_iteration_info() -> dict:
    logs = sorted(LOG_DIR.glob("iter-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    total = len(logs)
    latest = logs[0] if logs else None
    info = {"total": total, "latest": None, "latest_lines": 0, "latest_age": "", "latest_size": ""}
    if latest:
        info["latest"] = latest.name
        try:
            info["latest_lines"] = sum(1 for _ in open(latest))
        except Exception:
            pass
        mtime = latest.stat().st_mtime
        delta = time.time() - mtime
        if delta < 60:
            info["latest_age"] = f"{int(delta)}s ago"
        elif delta < 3600:
            info["latest_age"] = f"{int(delta / 60)}m ago"
        else:
            info["latest_age"] = f"{int(delta / 3600)}h {int((delta % 3600) / 60)}m ago"
        size_kb = latest.stat().st_size / 1024
        info["latest_size"] = f"{size_kb:.0f}KB" if size_kb > 1 else f"{latest.stat().st_size}B"
    return info


def get_ralph_log_events(n: int = 4) -> tuple[list[str], list[str]]:
    ralph_log = LOG_DIR / "ralph.log"
    if not ralph_log.exists():
        return [], []
    lines = ralph_log.read_text().splitlines()
    completions = [l for l in lines if "completed successfully" in l][-n:]
    failures = [l for l in lines if re.search(r"Failed|Credit|FATAL", l)][-3:]
    return completions, failures


def get_latest_log() -> Path | None:
    logs = sorted(LOG_DIR.glob("iter-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


# ── Log Viewer (scrollable) ────────────────────────────────────────────────


class LogViewer:
    """Loads the latest iteration log and supports scroll navigation."""

    def __init__(self):
        self._lock = threading.Lock()
        self._lines: list[str] = []
        self._current_path: Path | None = None
        self._scroll_offset: int = 0
        self._stop = threading.Event()
        self._total_lines = 0

    def start(self):
        self._reload()
        thread = threading.Thread(target=self._poll, daemon=True)
        thread.start()

    def stop(self):
        self._stop.set()

    def _reload(self):
        logs = sorted(LOG_DIR.glob("iter-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        latest = None
        for log in logs:
            if log.stat().st_size > 0:
                latest = log
                break
        if not latest:
            latest = logs[0] if logs else None
        if not latest:
            return
        try:
            text = latest.read_text(errors="replace")
            lines = text.splitlines()
            with self._lock:
                changed_file = latest != self._current_path
                self._current_path = latest
                self._lines = lines
                self._total_lines = len(lines)
                if changed_file:
                    self._scroll_offset = 0
        except Exception:
            pass

    def _poll(self):
        while not self._stop.is_set():
            self._stop.wait(2)
            if not self._stop.is_set():
                self._reload()

    def scroll_up(self, n: int = 3):
        with self._lock:
            self._scroll_offset = min(self._scroll_offset + n, max(0, self._total_lines - 1))

    def scroll_down(self, n: int = 3):
        with self._lock:
            self._scroll_offset = max(0, self._scroll_offset - n)

    def scroll_top(self):
        with self._lock:
            self._scroll_offset = max(0, self._total_lines - 1)

    def scroll_bottom(self):
        with self._lock:
            self._scroll_offset = 0

    def get_window(self, visible_lines: int) -> tuple[list[str], int, int, str | None]:
        with self._lock:
            total = self._total_lines
            name = self._current_path.name if self._current_path else None
            if not self._lines:
                return [], 0, 0, name
            end = total - self._scroll_offset
            start = max(0, end - visible_lines)
            return self._lines[start:end], self._scroll_offset, total, name


# ── Keyboard Reader ────────────────────────────────────────────────────────


class KeyReader:
    def __init__(self):
        self._stop = threading.Event()
        self._keys: list[str] = []
        self._lock = threading.Lock()
        self._old_settings = None

    def start(self):
        if not sys.stdin.isatty():
            return
        try:
            self._old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        except termios.error:
            return
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def stop(self):
        self._stop.set()
        if self._old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
            except termios.error:
                pass

    def get_keys(self) -> list[str]:
        with self._lock:
            keys = list(self._keys)
            self._keys.clear()
            return keys

    def _run(self):
        while not self._stop.is_set():
            try:
                ch = os.read(sys.stdin.fileno(), 3).decode("utf-8", errors="ignore")
                if ch:
                    with self._lock:
                        self._keys.append(ch)
            except (OSError, ValueError):
                break


# ── Dashboard Panels ───────────────────────────────────────────────────────

AMBER = "rgb(245,158,11)"
GOLD = "rgb(251,191,36)"
MUTED = "rgb(140,140,140)"
BORDER = "rgb(80,80,80)"


def make_header(epic_id: str) -> Panel:
    now = datetime.now().strftime("%H:%M:%S")
    t = Text()
    t.append("RALPH LOOP", style=f"bold {AMBER}")
    t.append(f"  {epic_id}", style=MUTED)
    t.append(f"  {now}", style=f"{MUTED} italic")
    t.append("    q", style="bold white")
    t.append("=quit ", style=MUTED)
    t.append("j/k", style="bold white")
    t.append("=scroll ", style=MUTED)
    t.append("g/G", style="bold white")
    t.append("=top/btm", style=MUTED)
    return Panel(t, box=box.HEAVY, style=BORDER, padding=(0, 1))


def _format_heartbeat(secs: float) -> tuple[str, str]:
    s = int(secs)
    if s < 60:
        label = f"{s}s"
    elif s < 3600:
        label = f"{s // 60}m {s % 60}s"
    else:
        label = f"{s // 3600}h {(s % 3600) // 60}m"
    if secs < 120:
        return label, "bold green"
    elif secs < 600:
        return label, f"bold {AMBER}"
    else:
        return label, "bold red"


def make_gauges(task_counts: dict, velocity: dict, iter_info: dict) -> Panel:
    t = Table.grid(padding=(0, 3))
    for _ in range(8):
        t.add_column(justify="center")

    hb_ts = velocity.get("heartbeat_ts", 0)
    hb_secs = time.time() - hb_ts if hb_ts > 0 else 9999
    hb_label, hb_style = _format_heartbeat(hb_secs)

    t.add_row(
        Text("CLOSED", style=MUTED), Text("REVIEW", style=MUTED),
        Text("ACTIVE", style=MUTED), Text("OPEN", style=MUTED),
        Text("ITERS", style=MUTED), Text("COMMITS/24h", style=MUTED),
        Text("LINES", style=MUTED), Text("LAST ACTIVITY", style=MUTED),
    )
    t.add_row(
        Text(str(task_counts["closed"]), style="bold green"),
        Text(str(task_counts["review"]), style="bold magenta"),
        Text(str(task_counts["active"]), style=f"bold {AMBER}"),
        Text(str(task_counts["open"]), style="white"),
        Text(str(iter_info["total"]), style="bold cyan"),
        Text(str(velocity["24h"]), style="bold cyan"),
        Text(f"+{velocity['ins']} -{velocity['dels']}",
             style="bold green" if velocity["ins"] > velocity["dels"] else "bold red"),
        Text(hb_label, style=hb_style),
    )
    return Panel(t, title=f"[{MUTED}]gauges[/]", box=box.ROUNDED, style=BORDER, padding=(0, 1))


def make_commits(commits: list[dict]) -> Panel:
    table = Table(box=None, show_header=True, header_style=MUTED, padding=(0, 1), expand=True)
    table.add_column("hash", style=GOLD, width=8, no_wrap=True)
    table.add_column("message", style="white", ratio=1)
    table.add_column("delta", justify="right", width=14, no_wrap=True)
    table.add_column("when", style=MUTED, justify="right", width=12, no_wrap=True)
    for c in commits:
        msg = Text(c["msg"][:65])
        for match in re.finditer(r"\(td-[a-f0-9]+\)", c["msg"][:65]):
            msg.stylize("cyan", match.start(), match.end())
        stat = Text(c["stat"] or "")
        for m in re.finditer(r"\+\d+", c["stat"]):
            stat.stylize("green", m.start(), m.end())
        for m in re.finditer(r"-\d+", c["stat"]):
            stat.stylize("red", m.start(), m.end())
        table.add_row(c["hash"], msg, stat, c["ago"])
    return Panel(table, title=f"[{MUTED}]commits[/]", box=box.ROUNDED, style=BORDER, padding=(0, 0))


def make_tasks(activities: list[dict], in_progress: list[str]) -> Panel:
    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("status", width=10, no_wrap=True)
    table.add_column("task", ratio=1)
    for line in in_progress:
        table.add_row(Text("ACTIVE", style=f"bold {AMBER}"), Text(line, style="bold white"))
    for a in activities:
        status = a["status"]
        if status == "closed":
            st = Text("CLOSED", style="green")
        elif status == "in_review":
            st = Text("REVIEW", style="magenta")
        elif status == "in_progress":
            st = Text("ACTIVE", style=AMBER)
        else:
            st = Text(status.upper(), style=MUTED)
        table.add_row(st, Text(f'{a["id"]}: {a["title"][:55]}', style="white"))
    if not activities and not in_progress:
        table.add_row(Text(""), Text("No recent activity", style=MUTED))
    return Panel(table, title=f"[{MUTED}]tasks[/]", box=box.ROUNDED, style=BORDER, padding=(0, 0))


def make_next_tasks(next_open: list[dict]) -> Panel:
    """Up-next panel showing the next tasks the loop will pick up."""
    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column("priority", width=5, no_wrap=True)
    table.add_column("task", ratio=1)
    table.add_column("type", width=8, no_wrap=True, justify="right")

    PRIORITY_STYLES = {"P0": "bold red", "P1": f"bold {AMBER}", "P2": "bold cyan", "P3": MUTED}

    for t in next_open:
        pstyle = PRIORITY_STYLES.get(t["priority"], MUTED)
        table.add_row(
            Text(t["priority"], style=pstyle),
            Text(f'{t["id"]}: {t["title"][:50]}', style="white"),
            Text(t["type"], style=MUTED),
        )

    if not next_open:
        table.add_row(Text(""), Text("No open tasks", style=MUTED), Text(""))

    return Panel(table, title=f"[{MUTED}]up next[/]", box=box.ROUNDED, style=BORDER, padding=(0, 0))


def make_velocity(velocity: dict) -> Panel:
    items = []
    max_val = max(velocity["1h"], velocity["6h"] / 6, velocity["24h"] / 24, 1)
    for label, count, window in [("1h", velocity["1h"], 1), ("6h", velocity["6h"], 6), ("24h", velocity["24h"], 24)]:
        rate = count / window
        bar_len = int((rate / max_val) * 15) if max_val > 0 else 0
        bar = "\u2588" * bar_len + "\u2591" * (15 - bar_len)
        t = Text()
        t.append(f" {label:>3} ", style=MUTED)
        t.append(bar, style=AMBER)
        t.append(f" {count}", style="bold white")
        t.append(f" ({rate:.1f}/h)", style=MUTED)
        items.append(t)
    t = Text()
    t.append("\n last ", style=MUTED)
    t.append(velocity["last"] or "?", style="bold white")
    items.append(t)
    return Panel(Group(*items), title=f"[{MUTED}]velocity[/]", box=box.ROUNDED, style=BORDER, padding=(0, 1))


def make_loop_status(iter_info: dict, completions: list[str], failures: list[str]) -> Panel:
    items = []
    t = Text()
    t.append(f" iterations: ", style=MUTED)
    t.append(str(iter_info["total"]), style="bold cyan")
    if iter_info["latest"]:
        t.append(f"  current: ", style=MUTED)
        t.append(iter_info["latest"], style="white")
        t.append(f" ({iter_info['latest_lines']} lines, {iter_info['latest_size']})", style=MUTED)
    items.append(t)
    if iter_info["latest_age"]:
        t2 = Text()
        t2.append(f" last write: ", style=MUTED)
        t2.append(iter_info["latest_age"], style="white")
        items.append(t2)
    if completions:
        items.append(Text(""))
        for c in completions[-3:]:
            short = c[-70:] if len(c) > 70 else c
            items.append(Text(f" {short}", style="green"))
    if failures:
        items.append(Text(""))
        for f in failures[-2:]:
            short = f[-70:] if len(f) > 70 else f
            items.append(Text(f" {short}", style="bold red"))
    return Panel(Group(*items), title=f"[{MUTED}]loop[/]", box=box.ROUNDED, style=BORDER, padding=(0, 0))


def make_log_viewer(log_lines, scroll_offset, total, filename, visible) -> Panel:
    content = Text()
    for line in log_lines:
        stripped = line.strip()
        if not stripped:
            content.append("\n")
            continue
        if re.search(r"error|Error|ERROR|FATAL|panic", stripped):
            content.append(stripped + "\n", style="bold red")
        elif re.search(r"warn|WARN|Warning", stripped):
            content.append(stripped + "\n", style="yellow")
        elif re.search(r"\u2713|success|completed|PASS", stripped):
            content.append(stripped + "\n", style="green")
        elif re.search(r"\*\*.*\*\*", stripped):
            content.append(stripped + "\n", style="bold white")
        elif re.search(r"^[\u2500\u2501\u2550\u254C]|^---", stripped):
            content.append(stripped + "\n", style=MUTED)
        else:
            content.append(stripped + "\n", style="white")
    if not content.plain.strip():
        content.append("No log content", style=f"{MUTED} italic")
    title_parts = []
    if filename:
        title_parts.append(f"[{MUTED}]{filename}[/]")
    if total > 0:
        pos = total - scroll_offset
        title_parts.append(f"[{MUTED}]line {pos}/{total}[/]")
        if scroll_offset > 0:
            title_parts.append(f"[{AMBER}]SCROLLED[/]")
    title = " ".join(title_parts) if title_parts else f"[{MUTED}]log[/]"
    return Panel(content, title=title, box=box.ROUNDED, style=BORDER, padding=(0, 1))


# ── Layout + Data Cache + Main ─────────────────────────────────────────────


def build_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="gauges", size=5),
        Layout(name="middle", size=14),
        Layout(name="bottom"),
    )
    layout["middle"].split_row(
        Layout(name="commits", ratio=3),
        Layout(name="sidebar", ratio=2),
    )
    layout["sidebar"].split_column(
        Layout(name="velocity", size=7),
        Layout(name="loop"),
    )
    layout["bottom"].split_row(
        Layout(name="log", ratio=3),
        Layout(name="tasks_col", ratio=2),
    )
    layout["tasks_col"].split_column(
        Layout(name="tasks", ratio=2),
        Layout(name="next_tasks", size=7),
    )
    return layout


class DataCache:
    def __init__(self, epic_id: str):
        self.epic_id = epic_id
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self.task_counts = {"closed": 0, "review": 0, "active": 0, "open": 0, "total": 0}
        self.velocity = {"1h": 0, "6h": 0, "24h": 0, "ins": 0, "dels": 0, "last": "", "heartbeat_ts": 0}
        self.commits: list[dict] = []
        self.activities: list[dict] = []
        self.in_progress: list[str] = []
        self.next_open: list[dict] = []
        self.iter_info = {"total": 0, "latest": None, "latest_lines": 0, "latest_age": "", "latest_size": ""}
        self.completions: list[str] = []
        self.failures: list[str] = []

    def refresh(self):
        epic = self.epic_id
        tc = {"closed": count_tasks(epic, "closed"), "review": count_tasks(epic, "in_review"),
              "active": count_tasks(epic, "in_progress"), "open": count_tasks(epic, "open")}
        tc["total"] = sum(tc.values())
        v = get_commit_velocity()
        c = get_recent_commits(8)
        a = get_recent_td_activity(epic, 6)
        ip = get_in_progress(epic)
        no = get_next_open_tasks(epic, 3)
        ii = get_iteration_info()
        comp, fail = get_ralph_log_events(4)
        with self._lock:
            self.task_counts, self.velocity, self.commits = tc, v, c
            self.activities, self.in_progress, self.next_open, self.iter_info = a, ip, no, ii
            self.completions, self.failures = comp, fail

    def start(self):
        self.refresh()
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.is_set():
            self._stop.wait(STATUS_REFRESH)
            if not self._stop.is_set():
                try:
                    self.refresh()
                except Exception:
                    pass

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "task_counts": dict(self.task_counts), "velocity": dict(self.velocity),
                "commits": list(self.commits), "activities": list(self.activities),
                "in_progress": list(self.in_progress), "next_open": list(self.next_open),
                "iter_info": dict(self.iter_info),
                "completions": list(self.completions), "failures": list(self.failures),
            }


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <epic-id>"); sys.exit(1)
    epic_id = sys.argv[1]
    if not LOG_DIR.exists():
        print(f"No log directory found at {LOG_DIR}"); sys.exit(1)

    console = Console()
    cache = DataCache(epic_id)
    log_viewer = LogViewer()
    keys = KeyReader()

    def cleanup():
        cache.stop(); log_viewer.stop(); keys.stop()

    signal.signal(signal.SIGINT, lambda *_: (cleanup(), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda *_: (cleanup(), sys.exit(0)))

    console.print(f"[{MUTED}]Loading dashboard for {epic_id}...[/]")
    cache.start(); log_viewer.start(); keys.start()

    layout = build_layout()
    LOG_VISIBLE_LINES = 25

    try:
        with Live(layout, console=console, refresh_per_second=2, screen=True) as live:
            while True:
                for key in keys.get_keys():
                    if key == "q": raise SystemExit(0)
                    elif key in ("j", "\x1b[B"): log_viewer.scroll_down(3)
                    elif key in ("k", "\x1b[A"): log_viewer.scroll_up(3)
                    elif key == "g": log_viewer.scroll_top()
                    elif key == "G": log_viewer.scroll_bottom()
                    elif key == "d": log_viewer.scroll_down(LOG_VISIBLE_LINES // 2)
                    elif key == "u": log_viewer.scroll_up(LOG_VISIBLE_LINES // 2)

                snap = cache.snapshot()
                ll, so, lt, ln = log_viewer.get_window(LOG_VISIBLE_LINES)
                layout["header"].update(make_header(epic_id))
                layout["gauges"].update(make_gauges(snap["task_counts"], snap["velocity"], snap["iter_info"]))
                layout["commits"].update(make_commits(snap["commits"]))
                layout["velocity"].update(make_velocity(snap["velocity"]))
                layout["loop"].update(make_loop_status(snap["iter_info"], snap["completions"], snap["failures"]))
                layout["log"].update(make_log_viewer(ll, so, lt, ln, LOG_VISIBLE_LINES))
                layout["tasks"].update(make_tasks(snap["activities"], snap["in_progress"]))
                layout["next_tasks"].update(make_next_tasks(snap["next_open"]))
                time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
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

### Loop Management

- **Timeout is essential (default 45min).** Without it, stuck iterations can block the loop indefinitely. The agent sometimes hangs waiting on an API response or enters a retry loop. Timeouts (exit code 124) are handled separately from real failures and don't count toward the consecutive failure budget.
- **Do NOT use `script -q` for log capture.** While it provides unbuffered output, `script` requires a controlling TTY. When ralph.sh runs in a non-interactive context, `script` gets stopped by `SIGTTIN`/`SIGTTOU` signals — the process enters state `T` (stopped), writes 0 bytes, and hangs forever. Use simple `> "$ITER_LOG" 2>&1` redirect instead. If you need unbuffered output, try `unbuffer` from `expect`.
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
| 0 lines in log, process state `T` | `script -q` stopped by TTY signal | Don't use `script` — use simple redirect `> log 2>&1` |
| Iteration runs for hours | Agent stuck on API/retry | Timeout handles this (exit 124), doesn't count as failure |
| Loop exits with Ctrl+C but no log entry | No signal trap | Signal trap logs "Stopped by signal" on SIGINT/SIGTERM |
| 22 tasks "in review" blocking everything | Agents don't close tasks | Add Step 0 review phase (in the template) |
| Agent rebuilds existing code | No codebase exploration step | Add "check what exists" instruction |
| Task works in dev, breaks in prod | No verification step | Require browser screenshots or test runs |
| Agent creates duplicate code | No awareness of sibling modules | Add "reuse from X module" section |
| Epic stalls with 0 unblocked tasks | All tasks blocked by unreviewed deps | Step 0 clears the review queue |
| Loop exits early while reviews pending | `has_open_tasks` doesn't count `in_review` | Include `in_review` in task count (in the template) |

### Monitoring

The dashboard (`ralph-tail.py`) shows everything at a glance — task gauges, commit velocity with lines changed, a live heartbeat timer, a scrollable log viewer, and an "up next" panel showing the next 3 tasks the loop will pick up by priority. The heartbeat (LAST ACTIVITY gauge) turns green/amber/red so you can tell at a glance if the loop is still working. Press `q` to quit, `j/k` to scroll the log.

For deeper monitoring:

```bash
# Check what's in each status
td list --epic <id> -s in_review    # Blocked until reviewed
td list --epic <id> -s open         # Available to pick up
td list --epic <id> -s in_progress  # Currently being worked on

# Kill a stuck iteration (loop recovers automatically)
kill <pid>

# Check git progress
git log --oneline --since="8 hours ago"
```

## Status File

Keep a `scripts/RALPH-STATUS.md` alongside the scripts as a handoff document for the next human or agent session. Include:

- Epic ID and branch
- Current loop state (iteration count, review backlog)
- Manual fixes applied outside the loop (so agents don't revert them)
- Key architecture docs to read
- Tasks added manually (not by the loop)
- What's blocked and why
- How to resume if the loop stops

This file is the fastest way to get context when picking up after a break or compaction.

## Setup from Scratch

For a new project:

1. Create the epic: `td epic create "My Feature"`
2. Create tasks under it with priorities and dependencies
3. Copy the scripts to `scripts/ralph.sh`, `scripts/ralph-tail.py`
4. Write `scripts/ralph-prompt.md` customized for your project
5. Create `scripts/RALPH-STATUS.md` with initial context
6. Run: `./scripts/ralph.sh <epic-id>`
7. Monitor: `./scripts/ralph-tail.py <epic-id>`

Optional: use a setup script (like `ralph-setup.sh`) that reads a plan/spec and creates tasks automatically with Claude.
