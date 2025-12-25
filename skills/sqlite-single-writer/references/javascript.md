# JavaScript/Node.js Implementation

## Dependencies

```json
{
  "dependencies": {
    "better-sqlite3": "^9.0.0",
    "proper-lockfile": "^4.1.2"
  }
}
```

Using `better-sqlite3` (synchronous) for simplicity. For async, use `sqlite3` with same pattern.

> **Note**: `proper-lockfile` uses directory-based locking, not OS-level `flock`. It handles stale locks via timestamps but won't auto-release on crash like native flock. For production, consider native addons or accept this tradeoff.

## Lock Implementation

```javascript
// lock.js
const fs = require('fs');
const path = require('path');
const lockfile = require('proper-lockfile');

const DEFAULT_TIMEOUT = 500; // ms
const INITIAL_BACKOFF = 5; // ms
const MAX_BACKOFF = 50; // ms

class LockTimeout extends Error {
  constructor(holder, timeoutMs) {
    super(
      `write lock timeout after ${timeoutMs}ms\n` +
      `  holder: ${holder}\n` +
      `  try again or check if holder process is stuck`
    );
    this.name = 'LockTimeout';
    this.holder = holder;
    this.timeoutMs = timeoutMs;
  }
}

class WriteLocker {
  constructor(baseDir) {
    this.lockPath = path.join(baseDir, 'db.lock');
    this.release = null;
  }

  async acquire(timeout = DEFAULT_TIMEOUT) {
    // Ensure lock file exists
    if (!fs.existsSync(this.lockPath)) {
      fs.writeFileSync(this.lockPath, '');
    }

    const deadline = Date.now() + timeout;
    let backoff = INITIAL_BACKOFF;

    while (true) {
      try {
        this.release = await lockfile.lock(this.lockPath, {
          stale: 10000, // Consider lock stale after 10s
          retries: 0,   // We handle retries ourselves
        });
        
        this._writeHolder();
        return;
      } catch (err) {
        if (Date.now() >= deadline) {
          const holder = this._readHolder();
          throw new LockTimeout(holder, timeout);
        }

        await this._sleep(backoff);
        backoff = Math.min(backoff * 2, MAX_BACKOFF);
      }
    }
  }

  async unlock() {
    if (this.release) {
      try {
        fs.truncateSync(this.lockPath, 0);
      } catch (e) {}
      
      await this.release();
      this.release = null;
    }
  }

  _writeHolder() {
    const info = `pid:${process.pid}\ntime:${new Date().toISOString()}\n`;
    fs.writeFileSync(this.lockPath, info);
  }

  _readHolder() {
    try {
      return fs.readFileSync(this.lockPath, 'utf8').trim();
    } catch (e) {
      return 'unknown';
    }
  }

  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = { WriteLocker, LockTimeout };
```

## Database Integration

```javascript
// db.js
const Database = require('better-sqlite3');
const path = require('path');
const { WriteLocker } = require('./lock');

class DB {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.baseDir = path.dirname(dbPath);
    this.db = new Database(dbPath);
    
    // Enable WAL mode
    this.db.pragma('journal_mode = WAL');
    this.db.pragma('busy_timeout = 500');
    this.db.pragma('synchronous = NORMAL');
  }

  close() {
    this.db.close();
  }

  async withWriteLock(fn) {
    const locker = new WriteLocker(this.baseDir);
    await locker.acquire();
    try {
      return fn();
    } finally {
      await locker.unlock();
    }
  }

  // Write operations need lock
  async createRecord(name, value) {
    return this.withWriteLock(() => {
      const stmt = this.db.prepare(
        'INSERT INTO records (name, value) VALUES (?, ?)'
      );
      const result = stmt.run(name, value);
      return result.lastInsertRowid;
    });
  }

  async updateRecord(id, value) {
    return this.withWriteLock(() => {
      const stmt = this.db.prepare(
        'UPDATE records SET value = ? WHERE id = ?'
      );
      stmt.run(value, id);
    });
  }

  // Reads don't need lock with WAL
  getRecord(id) {
    const stmt = this.db.prepare(
      'SELECT id, name, value FROM records WHERE id = ?'
    );
    return stmt.get(id);
  }

  getAllRecords() {
    const stmt = this.db.prepare('SELECT * FROM records');
    return stmt.all();
  }
}

module.exports = { DB };
```

## Usage Example

```javascript
const { DB } = require('./db');
const { LockTimeout } = require('./lock');

async function main() {
  const db = new DB('./data/app.db');

  try {
    // Write with lock
    const id = await db.createRecord('test', 42);
    console.log('Created record:', id);

    // Read without lock
    const record = db.getRecord(id);
    console.log('Record:', record);

  } catch (err) {
    if (err instanceof LockTimeout) {
      console.error('Write failed, try again:', err.message);
    } else {
      throw err;
    }
  } finally {
    db.close();
  }
}

main();
```

## Alternative: Native Flock (Unix only)

For true OS-level locking, use a native addon like `fs-ext`:

```bash
npm install fs-ext
```

```javascript
const fs = require('fs');
const { flockSync } = require('fs-ext');

function tryLockExclusive(fd) {
  try {
    flockSync(fd, 'exnb'); // exclusive, non-blocking
    return true;
  } catch (e) {
    if (e.code === 'EAGAIN') return false;
    throw e;
  }
}

function unlock(fd) {
  flockSync(fd, 'un');
}
```

This provides true auto-release on crash but only works on Unix.
