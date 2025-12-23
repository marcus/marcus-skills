---
name: cursor-agent-orchestrator
description: Build Python orchestrators that spawn multiple cursor-agent processes in parallel, capture their output, handle timeouts, log results, and verify task completion. Use this skill when automating bulk tasks via cursor-agent from the terminal.
metadata:
  author: marcus-vorwaller
  version: "1.0"
---

# Cursor Agent Orchestrator

You are building a **Python orchestrator** that spawns one or more `cursor-agent` CLI processes, captures their output, handles errors/timeouts, and logs structured results.

The goal: run cursor-agent at scale to process a batch of tasks (files, database rows, API requests, etc.) with:

- **Parallel execution** with controlled concurrency
- **Timeout enforcement** so hung agents don't block forever
- **Structured logging** (JSONL) for analysis and retry
- **Transcript capture** for debugging failed runs
- **Graceful shutdown** on Ctrl+C

---

## When to use this skill

Use this skill when the user asks for:

- Batch processing using cursor-agent (analyzing files, generating docs, migrating code)
- Parallel agent orchestration with concurrency limits
- Automating cursor-agent runs from Python scripts
- Capturing agent output for logging, verification, or debugging

Do **not** use this skill for:

- Interactive cursor-agent usage (just run it directly)
- Single one-off agent invocations (use `subprocess.run` or the shell)
- Non-cursor-agent automation tasks

---

## Inputs you should gather (from the user or context)

Before building an orchestrator, infer or ask (only if needed):

1. **Work items**
   - What are we processing? (files, database rows, API endpoints, etc.)
   - How do we get the next item? (query DB, list directory, read CSV)
   - How do we know an item is complete? (file exists, DB field set, API returns 200)

2. **Prompt template**
   - What prompt should each agent receive?
   - What variables need to be injected? (file path, item ID, name, etc.)

3. **Concurrency & timing**
   - How many agents should run in parallel? (default: 3)
   - What's the timeout per task? (default: 15 minutes)

4. **Verification**
   - How do we verify the agent completed successfully?
   - What artifacts should exist after completion?

5. **Output requirements**
   - Where should logs go? (JSONL file, database, stdout)
   - Should transcripts be saved for debugging?

---

## Output expectations

When this skill is active, you should produce:

- A **complete Python script** with:
  - Async orchestration using `asyncio`
  - Configurable CLI via `argparse`
  - Work item leasing/tracking
  - Agent spawning with proper flags
  - Output capture and parsing
  - Timeout handling
  - Structured logging
  - Graceful shutdown

- **Clear documentation** of:
  - How to run the script
  - What each CLI flag does
  - How to monitor progress
  - How to retry failed items

---

## Architecture

### Core components

```
┌─────────────────────────────────────────────────────────────────┐
│  Orchestrator                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Config        - CLI args, paths, timeouts, concurrency        │
│  WorkItem      - Dataclass for items to process                 │
│  WorkerTask    - Tracks running agent (process, output, timing) │
│  Stats         - Success/failed/timeout counters                │
├─────────────────────────────────────────────────────────────────┤
│  lease_next_item()     - Get next available work item           │
│  build_prompt()        - Inject variables into prompt template  │
│  spawn_agent()         - Start cursor-agent subprocess          │
│  verify_completion()   - Check if agent succeeded               │
│  log_result()          - Write JSONL log entry                  │
│  save_transcript()     - Save agent stdout/stderr               │
└─────────────────────────────────────────────────────────────────┘
```

### Worker loop

Each worker runs this loop until shutdown or no work remains:

```
while not shutdown_requested:
    1. Lease next work item (with lock if concurrent)
    2. Build prompt from template + item context
    3. Spawn cursor-agent subprocess
    4. Wait for completion or timeout
    5. Capture stdout/stderr
    6. Verify completion (check DB/files/etc.)
    7. Log result (success/failed/timeout)
    8. Save transcript
    9. Release lock if failed
```

---

## cursor-agent CLI reference

### Essential flags

```bash
cursor-agent agent \
    --print \                    # Print output to stdout (required)
    --output-format stream-json \ # Structured JSON output (recommended)
    --model <model-name> \       # Model to use (e.g., claude-sonnet-4-20250514)
    --workspace <path> \         # Working directory for the agent
    --force \                    # Skip confirmation prompts
    --approve-mcps \             # Auto-approve MCP servers
    "<prompt>"                   # The prompt (as final positional arg)
```

### Output format: stream-json

When using `--output-format stream-json`, stdout contains newline-delimited JSON events:

| Event type | Subtype | Description |
|------------|---------|-------------|
| `thinking` | `delta` | Streaming thinking text |
| `tool_call` | `started` | Tool invocation started |
| `tool_call` | `completed` | Tool invocation finished |
| `assistant` | - | Assistant message content |
| `result` | - | Final result (may include `is_error: true`) |

### Parsing tool calls

Tool call events contain nested structures:

```json
{
  "type": "tool_call",
  "subtype": "started",
  "tool_call": {
    "shellToolCall": {
      "args": { "command": "ls -la" }
    }
  }
}
```

Common tool types:
- `shellToolCall` → `args.command`
- `readFileToolCall` → `args.path`
- `writeFileToolCall` / `editFileToolCall` → `args.path` or `args.filePath`
- `lsToolCall` → `args.path`
- `grepToolCall` → `args.pattern`

---

## Implementation patterns

### 1. Dataclasses for state

```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import asyncio

@dataclass
class WorkItem:
    """Represents a unit of work to process."""
    id: int
    name: str
    path: str
    # Add fields relevant to your use case

@dataclass
class WorkerTask:
    """Tracks a running agent task."""
    worker_id: str
    item: WorkItem
    process: Optional[asyncio.subprocess.Process]
    start_time: datetime
    stdout_lines: List[str]
    stderr_lines: List[str]

@dataclass
class Config:
    """Orchestrator configuration."""
    concurrency: int
    timeout_min: int
    max_items: int
    model: str
    log_path: Path
    transcripts_dir: Path
    workspace: Path
    dry_run: bool
    run_id: str
    verbose: bool
    heartbeat_interval: int
```

### 2. Async subprocess spawning

```python
async def spawn_agent(prompt: str, config: Config) -> asyncio.subprocess.Process:
    """Spawn cursor-agent with the given prompt."""
    cmd = [
        'cursor-agent',
        'agent',
        '--print',
        '--output-format', 'stream-json',
        '--model', config.model,
        '--workspace', str(config.workspace),
        '--force',
        '--approve-mcps',
        prompt
    ]
    
    return await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
```

### 3. Timeout handling with communicate()

```python
async def run_with_timeout(process, timeout_seconds: int):
    """
    Run process with timeout, capturing all output.
    
    Use communicate() instead of reading streams directly - 
    this properly handles pipe buffering and prevents deadlocks.
    """
    try:
        stdout_data, stderr_data = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout_seconds
        )
        return {
            'stdout': stdout_data.decode('utf-8', errors='replace').splitlines(),
            'stderr': stderr_data.decode('utf-8', errors='replace').splitlines(),
            'exit_code': process.returncode,
            'timed_out': False
        }
    except asyncio.TimeoutError:
        # Kill the process
        process.terminate()
        await asyncio.sleep(2)
        if process.returncode is None:
            process.kill()
        
        # Try to get partial output
        try:
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(),
                timeout=5
            )
            stdout_lines = stdout_data.decode('utf-8', errors='replace').splitlines()
            stderr_lines = stderr_data.decode('utf-8', errors='replace').splitlines()
        except:
            stdout_lines = []
            stderr_lines = []
        
        return {
            'stdout': stdout_lines,
            'stderr': stderr_lines,
            'exit_code': None,
            'timed_out': True
        }
```

### 4. Concurrency control with semaphore

```python
async def run_orchestrator(config: Config):
    """Main orchestrator - spawns worker pool."""
    semaphore = asyncio.Semaphore(config.concurrency)
    
    workers = [
        asyncio.create_task(worker(f"worker-{i}", semaphore, config))
        for i in range(config.concurrency)
    ]
    
    await asyncio.gather(*workers, return_exceptions=True)
```

### 5. Worker loop with proper locking

```python
async def worker(worker_id: str, semaphore: asyncio.Semaphore, config: Config):
    """Worker coroutine - processes items until exhausted."""
    global shutdown_requested
    
    while not shutdown_requested:
        async with semaphore:
            # Lease next item
            item = lease_next_item(config.run_id, worker_id, config)
            
            if not item:
                log_console(f"[{worker_id}] No more items available")
                break
            
            log_console(f"[{worker_id}] STARTED {item.name}")
            
            # Build prompt
            prompt = build_prompt(item, config)
            
            # Create task tracking object
            task = WorkerTask(
                worker_id=worker_id,
                item=item,
                process=None,
                start_time=datetime.now(timezone.utc),
                stdout_lines=[],
                stderr_lines=[]
            )
            
            try:
                # Spawn and wait
                task.process = await spawn_agent(prompt, config)
                result = await run_with_timeout(task.process, config.timeout_min * 60)
                
                task.stdout_lines = result['stdout']
                task.stderr_lines = result['stderr']
                
                if result['timed_out']:
                    log_console(f"[{worker_id}] TIMEOUT {item.name}", 'TIMEOUT')
                    await log_result(task, 'timeout', config)
                else:
                    # Verify completion
                    success, reason = verify_completion(item)
                    
                    if success:
                        log_console(f"[{worker_id}] SUCCESS {item.name}", 'SUCCESS')
                        await log_result(task, 'success', config)
                    else:
                        log_console(f"[{worker_id}] FAILED {item.name}: {reason}", 'FAILED')
                        await log_result(task, 'failed', config)
                
                # Save transcript
                await save_transcript(task, config)
                
            except Exception as e:
                log_console(f"[{worker_id}] ERROR {item.name}: {e}", 'ERROR')
                await log_result(task, 'failed', config)
```

### 6. JSONL logging

```python
import json
from datetime import datetime, timezone

async def log_result(task: WorkerTask, status: str, config: Config):
    """Append structured result to JSONL log file."""
    duration_s = int((datetime.now(timezone.utc) - task.start_time).total_seconds())
    
    result = {
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'run_id': config.run_id,
        'worker_id': task.worker_id,
        'item_id': task.item.id,
        'item_name': task.item.name,
        'status': status,  # 'success', 'failed', 'timeout'
        'duration_s': duration_s,
    }
    
    config.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with io_lock:
        with open(config.log_path, 'a') as f:
            f.write(json.dumps(result) + '\n')
```

### 7. Transcript parsing

```python
def parse_stream_json_transcript(stdout_lines: List[str]) -> str:
    """
    Parse stream-json output into human-readable transcript.
    
    Extracts thinking, tool calls, and assistant messages.
    """
    output = []
    
    for line in stdout_lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            event_type = event.get('type', '')
            subtype = event.get('subtype', '')
            
            if event_type == 'thinking' and subtype == 'delta':
                text = event.get('text', '').strip()
                if text:
                    output.append(f"[THINKING] {text}")
            
            elif event_type == 'tool_call':
                if subtype == 'started':
                    tool_call = event.get('tool_call', {})
                    for tool_name, tool_data in tool_call.items():
                        args = tool_data.get('args', {})
                        if 'shellToolCall' in tool_call:
                            output.append(f"[TOOL:shell] {args.get('command', '')}")
                        elif 'readFileToolCall' in tool_call:
                            output.append(f"[TOOL:read] {args.get('path', '')}")
                        elif 'writeFileToolCall' in tool_call:
                            output.append(f"[TOOL:write] {args.get('path', '')}")
                        else:
                            output.append(f"[TOOL:{tool_name}] {json.dumps(args)[:200]}")
                        break
                
                elif subtype == 'completed':
                    tool_call = event.get('tool_call', {})
                    for _, tool_data in tool_call.items():
                        result = tool_data.get('result', {})
                        if 'success' in result:
                            exit_code = result['success'].get('exitCode', 0)
                            stdout = result['success'].get('stdout', '')[:200]
                            output.append(f"  -> exit={exit_code}: {stdout}")
                        elif 'error' in result:
                            output.append(f"  -> ERROR: {str(result['error'])[:200]}")
                        break
            
            elif event_type == 'assistant':
                content = event.get('message', {}).get('content', [])
                for item in content:
                    if item.get('type') == 'text':
                        output.append(f"[ASSISTANT] {item.get('text', '')[:500]}")
            
            elif event_type == 'result':
                is_error = event.get('is_error', False)
                result_text = event.get('result', '')[:500]
                prefix = '[RESULT:ERROR]' if is_error else '[RESULT]'
                output.append(f"{prefix} {result_text}")
                
        except json.JSONDecodeError:
            if line.strip():
                output.append(line)
    
    return '\n'.join(output)
```

### 8. Graceful shutdown

```python
import signal
import sys

shutdown_requested = False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    global shutdown_requested
    
    if shutdown_requested:
        print("Force quit requested")
        sys.exit(1)
    
    print("Shutdown requested. Waiting for active tasks to complete...")
    print("Press Ctrl+C again to force quit.")
    shutdown_requested = True

# In main():
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 9. Heartbeat for long-running tasks

```python
async def heartbeat_loop(task: WorkerTask, interval: int):
    """Print periodic elapsed time while task is running."""
    try:
        while True:
            await asyncio.sleep(interval)
            elapsed = datetime.now(timezone.utc) - task.start_time
            mins, secs = divmod(int(elapsed.total_seconds()), 60)
            log_console(f"[{task.worker_id}] ... {mins}m {secs}s elapsed")
    except asyncio.CancelledError:
        pass  # Task completed, stop heartbeat

# In worker loop:
heartbeat_task = asyncio.create_task(heartbeat_loop(task, config.heartbeat_interval))
try:
    # ... run agent ...
finally:
    heartbeat_task.cancel()
    try:
        await heartbeat_task
    except asyncio.CancelledError:
        pass
```

### 10. Work item locking (for database-backed queues)

```python
def lease_next_item(run_id: str, worker_id: str, config: Config) -> Optional[WorkItem]:
    """
    Atomically find and lock the next eligible item.
    
    Uses an atomic UPDATE to prevent race conditions between workers.
    """
    db = get_session()
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=config.lock_ttl_min)
        lock_owner = f"{run_id}/{worker_id}"
        
        # Atomic: update where not locked or lock is stale
        # Use a subquery to select the candidate ID
        candidate_id = (
            select(Item.id)
            .where(
                Item.completed_at.is_(None),
                or_(
                    Item.locked_at.is_(None),
                    Item.locked_at < cutoff_time,
                ),
            )
            .order_by(Item.id.asc())
            .limit(1)
            .scalar_subquery()
        )
        
        result = db.execute(
            update(Item)
            .where(Item.id == candidate_id)
            .values(locked_at=datetime.now(timezone.utc), locked_by=lock_owner)
        )
        db.commit()
        
        if result.rowcount == 0:
            return None
        
        # Fetch the locked item
        item = db.query(Item).filter(Item.locked_by == lock_owner).first()
        return WorkItem(id=item.id, name=item.name, path=item.path)
        
    finally:
        db.close()


def release_lock(item_id: int, run_id: str, worker_id: str):
    """Release lock if we are the owner (on failure)."""
    db = get_session()
    try:
        lock_owner = f"{run_id}/{worker_id}"
        db.execute(
            update(Item)
            .where(Item.id == item_id, Item.locked_by == lock_owner)
            .values(locked_at=None, locked_by=None)
        )
        db.commit()
    finally:
        db.close()
```

---

## CLI structure

```python
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Run cursor-agent workers to process batch tasks"
    )
    
    parser.add_argument(
        '--concurrency', type=int, default=3,
        help='Number of concurrent workers (default: 3)'
    )
    
    parser.add_argument(
        '--timeout-min', type=int, default=15,
        help='Timeout per task in minutes (default: 15)'
    )
    
    parser.add_argument(
        '--max-items', type=int, default=0,
        help='Max items to process, 0=unlimited (default: 0)'
    )
    
    parser.add_argument(
        '--model', default='claude-sonnet-4-20250514',
        help='Model for cursor-agent'
    )
    
    parser.add_argument(
        '--log-path', type=Path, default=None,
        help='JSONL log file path'
    )
    
    parser.add_argument(
        '--transcripts-dir', type=Path, default=Path('logs/transcripts'),
        help='Directory for agent transcripts'
    )
    
    parser.add_argument(
        '--workspace', type=Path, required=True,
        help='Workspace directory for cursor-agent'
    )
    
    parser.add_argument(
        '--verbose', action='store_true',
        help='Show detailed subprocess output'
    )
    
    parser.add_argument(
        '--heartbeat-interval', type=int, default=30,
        help='Seconds between heartbeat logs (0 to disable)'
    )
    
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Show what would be processed without running agents'
    )
    
    args = parser.parse_args()
    
    # Generate unique run ID
    run_id = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S') + '_' + str(uuid.uuid4())[:8]
    
    # Build config and run
    config = Config(...)
    asyncio.run(run_orchestrator(config))
```

---

## Best practices

### Do

- **Use `asyncio.create_subprocess_exec`** - Not `subprocess.run` for async
- **Use `communicate()` for output capture** - Prevents pipe buffer deadlocks
- **Always set timeouts** - Agents can hang indefinitely
- **Use atomic locking** - Prevent race conditions with UPDATE...WHERE
- **Generate unique run IDs** - `YYYYMMDD_HHMMSS_uuid[:8]` pattern
- **Save transcripts per run** - Organize by `transcripts/{run_id}/{item_id}.txt`
- **Log to JSONL** - Easy to grep, parse, and analyze
- **Handle SIGINT/SIGTERM** - Allow graceful shutdown
- **Use UTC timestamps everywhere** - Avoid timezone confusion
- **Anchor relative paths to project root** - Makes running from anywhere predictable

### Don't

- **Don't read stdout/stderr streams directly** - Use `communicate()` to avoid deadlocks
- **Don't skip verification** - Always check that the agent actually completed the task
- **Don't hardcode concurrency** - Make it configurable via CLI
- **Don't forget to release locks on failure** - Or items will be stuck until lock TTL expires
- **Don't kill processes without trying terminate first** - Give them a chance to cleanup
- **Don't mix sync and async database calls** - Use sync for simplicity or fully async

---

## Common issues and solutions

### Issue: Pipe buffer deadlock

**Symptom**: Agent hangs even though it completed

**Cause**: Reading stdout/stderr streams separately can deadlock if buffers fill

**Solution**: Use `process.communicate()` which handles both streams properly

### Issue: Race condition in item leasing

**Symptom**: Multiple workers process the same item

**Cause**: SELECT then UPDATE is not atomic

**Solution**: Use single UPDATE with subquery to atomically claim items

### Issue: Orphaned locks after crash

**Symptom**: Items stuck as locked even though no worker is processing them

**Cause**: Process died before releasing lock

**Solution**: Use lock TTL - consider locks stale after N minutes

### Issue: Agent output is truncated

**Symptom**: Transcripts end mid-stream

**Cause**: Process was killed before output was flushed

**Solution**: Try to read remaining output after kill with short timeout

### Issue: Cannot verify completion

**Symptom**: Success rate is 0% even though agents ran

**Cause**: Verification logic doesn't match what agent actually does

**Solution**: Check DB/file state that agent modifies, not just exit code

---

## Step-by-step workflow for the agent

When asked to build a cursor-agent orchestrator:

1. **Understand the work items**
   - What data source provides items? (DB, files, API)
   - What fields identify each item?
   - How do we know an item is done?

2. **Design the prompt template**
   - What context does the agent need?
   - What variables to inject?
   - Where is the template stored?

3. **Implement the core dataclasses**
   - `WorkItem`, `WorkerTask`, `Config`, `Stats`

4. **Implement work item management**
   - `lease_next_item()` with atomic locking
   - `release_lock()` for failed items
   - `verify_completion()` to check success

5. **Implement agent spawning**
   - Build command with proper flags
   - Handle timeout with `communicate()`
   - Parse stream-json output

6. **Implement logging**
   - JSONL result logging
   - Transcript saving
   - Console progress output

7. **Wire up the CLI**
   - Add all configuration flags
   - Set up signal handlers
   - Generate run ID

8. **Test with dry-run mode**
   - Verify item selection works
   - Check prompt generation
   - Confirm paths are correct

Always prioritize **reliability over speed** - a slower orchestrator that completes all tasks correctly is better than a fast one that silently fails.

