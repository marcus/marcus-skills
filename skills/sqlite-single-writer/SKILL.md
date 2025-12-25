---
name: sqlite-single-writer
description: Implement single-writer queue pattern for SQLite in multi-process environments. Use when building CLI tools, local apps, or agent systems where multiple processes may write to SQLite concurrently. Covers file locking (flock/LockFileEx), WAL mode, timeout handling, and diagnostic error messages. Works for Go, Rust, Python, JavaScript/Node.
metadata:
  author: marcus-vorwaller
  version: "1.0"
---

# SQLite Single-Writer Pattern

## Problem

SQLite supports one writer at a time. When multiple processes (not threads) attempt concurrent writes, you get `SQLITE_BUSY` errors. This skill provides a cross-platform locking pattern that:

- Serializes writes across processes
- Keeps reads concurrent and fast
- Provides diagnostic errors on timeout
- Automatically releases locks on crash

## Architecture

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Process 1  │  │  Process 2  │  │  Process 3  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
              ┌─────────▼─────────┐
              │  Write Lock File  │  ← flock/LockFileEx
              │   (db.lock)       │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │  SQLite (WAL)     │  ← Concurrent reads OK
              │   (data.db)       │
              └───────────────────┘
```

## Implementation Steps

### 1. Enable WAL Mode

WAL (Write-Ahead Logging) allows concurrent reads while writes are serialized.

```sql
PRAGMA journal_mode=WAL;
PRAGMA busy_timeout=500;      -- Fallback timeout (ms)
PRAGMA synchronous=NORMAL;    -- Faster, still safe with WAL
```

Run these on every database open.

### 2. Create Lock File

Use a separate lock file (not the database file) for coordination:

```
project/
├── data.db        # SQLite database
├── data.db-wal    # WAL file (auto-created)
├── data.db-shm    # Shared memory (auto-created)
└── db.lock        # Write lock file
```

### 3. Lock Acquisition Pattern

```
acquire(timeout):
    open("db.lock", CREATE | RDWR)
    deadline = now + timeout
    backoff = 5ms
    
    loop:
        if try_exclusive_lock():      # Non-blocking
            write_holder_info()       # PID + timestamp
            return SUCCESS
        
        if now > deadline:
            holder = read_holder_info()
            return TIMEOUT_ERROR(holder)
        
        sleep(backoff)
        backoff = min(backoff * 2, 50ms)  # Exponential, capped
```

### 4. Platform-Specific Locking

**Unix (flock):**
```c
flock(fd, LOCK_EX | LOCK_NB)  // Acquire
flock(fd, LOCK_UN)            // Release
```

**Windows (LockFileEx):**
```c
LockFileEx(handle, LOCKFILE_EXCLUSIVE_LOCK | LOCKFILE_FAIL_IMMEDIATELY, ...)
UnlockFileEx(handle, ...)
```

Both auto-release on process exit/crash.

### 5. Holder Info for Diagnostics

Write to lock file when acquired:
```
pid:12345
time:2025-01-15T10:30:45Z
```

On timeout, read and report:
```
write lock timeout after 500ms
  holder: pid:12345 since 2025-01-15T10:30:45Z
  try again or check if holder process is stuck
```

### 6. Wrap Write Operations

Every write method should:
1. Acquire lock (with timeout)
2. Execute write
3. Release lock (in finally/defer)

## Language-Specific References

See references for implementation details:

- [go.md](references/go.md) - Go implementation with flock/LockFileEx
- [rust.md](references/rust.md) - Rust implementation with fs2/windows-sys  
- [python.md](references/python.md) - Python implementation with fcntl/msvcrt
- [javascript.md](references/javascript.md) - Node.js implementation with proper-lockfile

## Key Parameters

| Parameter | Recommended | Notes |
|-----------|-------------|-------|
| Lock timeout | 500ms | Enough for small writes, fails fast |
| Initial backoff | 5ms | Start small |
| Max backoff | 50ms | Cap to avoid long waits |
| Busy timeout | 500ms | SQLite fallback, match lock timeout |

## Failure Modes

| Failure | Behavior | User Action |
|---------|----------|-------------|
| Lock timeout | Error with holder info | Retry or check stuck process |
| Process crash | Lock auto-released by OS | None needed |
| Stale lock file | Content stale, lock released | None (flock is source of truth) |

## Testing

Spawn N processes doing M writes each. Verify:
1. All N×M writes succeed (no lost writes)
2. Timeout errors include diagnostic info
3. Lock released after crash (kill -9 a holder)

```bash
# Example stress test
for i in {1..5}; do
    (for j in {1..10}; do ./app write "p$i-w$j"; done) &
done
wait
./app count  # Should be 50
```

## Common Mistakes

1. **Locking the database file** - Use separate lock file; SQLite manages its own locks
2. **Forgetting WAL mode** - Without WAL, readers block on writers too  
3. **Too long timeout** - 500ms is plenty; fail fast, let caller retry
4. **No holder info** - Without diagnostics, debugging contention is painful
5. **Thread locks for processes** - Mutex/RwLock don't work across processes; use flock
6. **Network filesystems** - `flock` may not work on NFS/SMB; use local filesystems only
7. **Ignoring EINTR** - Unix flock can be interrupted by signals; retry on EINTR
