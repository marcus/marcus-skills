# Python Implementation

## Dependencies

```
sqlite3  # Built-in
```

## Lock Implementation

```python
# lock.py
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

if sys.platform == 'win32':
    import msvcrt
else:
    import fcntl

DEFAULT_TIMEOUT = 0.5  # 500ms
INITIAL_BACKOFF = 0.005  # 5ms
MAX_BACKOFF = 0.05  # 50ms


class LockTimeout(Exception):
    def __init__(self, holder: str, timeout_s: float):
        self.holder = holder
        self.timeout_s = timeout_s
        timeout_ms = int(timeout_s * 1000)
        super().__init__(
            f"write lock timeout after {timeout_ms}ms\n"
            f"  holder: {holder}\n"
            f"  try again or check if holder process is stuck"
        )


class WriteLocker:
    def __init__(self, base_dir: str):
        self.lock_path = Path(base_dir) / "db.lock"
        self.lock_file = None

    def acquire(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self.lock_file = open(self.lock_path, 'a+')
        
        deadline = time.monotonic() + timeout
        backoff = INITIAL_BACKOFF

        while True:
            if self._try_lock():
                self._write_holder()
                return

            if time.monotonic() >= deadline:
                holder = self._read_holder()
                self.lock_file.close()
                self.lock_file = None
                raise LockTimeout(holder, timeout)

            time.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)

    def release(self) -> None:
        if self.lock_file is None:
            return
        
        try:
            self.lock_file.truncate(0)
            self._unlock()
        finally:
            self.lock_file.close()
            self.lock_file = None

    def _try_lock(self) -> bool:
        try:
            if sys.platform == 'win32':
                # Windows: locks 1 byte (sufficient for coordination)
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError) as e:
            # EINTR: interrupted by signal, caller should retry
            if getattr(e, 'errno', None) == 4:  # EINTR
                return False
            return False

    def _unlock(self) -> None:
        if sys.platform == 'win32':
            try:
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        else:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)

    def _write_holder(self) -> None:
        self.lock_file.seek(0)
        self.lock_file.truncate()
        self.lock_file.write(f"pid:{os.getpid()}\n")
        self.lock_file.write(f"time:{datetime.utcnow().isoformat()}Z\n")
        self.lock_file.flush()

    def _read_holder(self) -> str:
        try:
            return self.lock_path.read_text().strip()
        except Exception:
            return "unknown"

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()
```

## Database Integration

```python
# db.py
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from lock import WriteLocker, DEFAULT_TIMEOUT


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.base_dir = str(Path(db_path).parent)
        self.conn = sqlite3.connect(db_path)
        
        # Enable WAL mode
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=500")
        self.conn.execute("PRAGMA synchronous=NORMAL")

    def close(self):
        self.conn.close()

    @contextmanager
    def write_lock(self):
        locker = WriteLocker(self.base_dir)
        locker.acquire(DEFAULT_TIMEOUT)
        try:
            yield
        finally:
            locker.release()

    def create_record(self, name: str, value: int) -> int:
        with self.write_lock():
            cursor = self.conn.execute(
                "INSERT INTO records (name, value) VALUES (?, ?)",
                (name, value)
            )
            self.conn.commit()
            return cursor.lastrowid

    def update_record(self, id: int, value: int) -> None:
        with self.write_lock():
            self.conn.execute(
                "UPDATE records SET value = ? WHERE id = ?",
                (value, id)
            )
            self.conn.commit()

    def get_record(self, id: int) -> tuple:
        # Reads don't need lock with WAL mode
        cursor = self.conn.execute(
            "SELECT id, name, value FROM records WHERE id = ?",
            (id,)
        )
        return cursor.fetchone()
```

## Usage Example

```python
from db import Database

db = Database("./data/app.db")

try:
    # This acquires lock, writes, releases
    record_id = db.create_record("test", 42)
    
    # Reads don't need lock
    record = db.get_record(record_id)
    print(record)
    
except LockTimeout as e:
    print(f"Write failed: {e}")
    # Caller can retry

finally:
    db.close()
```
