# Rust Implementation

## Dependencies

```toml
[dependencies]
rusqlite = { version = "0.31", features = ["bundled"] }
fs2 = "0.4"       # Cross-platform file locking
chrono = "0.4"    # Timestamp formatting
```

## Lock Implementation

```rust
// lock.rs
use std::fs::{File, OpenOptions};
use std::io::{Read, Seek, SeekFrom, Write};
use std::path::PathBuf;
use std::time::{Duration, Instant};
use std::thread::sleep;
use fs2::FileExt;

const DEFAULT_TIMEOUT: Duration = Duration::from_millis(500);
const INITIAL_BACKOFF: Duration = Duration::from_millis(5);
const MAX_BACKOFF: Duration = Duration::from_millis(50);

pub struct WriteLocker {
    lock_path: PathBuf,
    lock_file: Option<File>,
}

#[derive(Debug)]
pub enum LockError {
    Io(std::io::Error),
    Timeout { holder: String },
}

impl WriteLocker {
    pub fn new(base_dir: &str) -> Self {
        Self {
            lock_path: PathBuf::from(base_dir).join("db.lock"),
            lock_file: None,
        }
    }

    pub fn acquire(&mut self, timeout: Duration) -> Result<(), LockError> {
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(&self.lock_path)
            .map_err(LockError::Io)?;

        let deadline = Instant::now() + timeout;
        let mut backoff = INITIAL_BACKOFF;

        loop {
            // Try non-blocking exclusive lock
            match file.try_lock_exclusive() {
                Ok(()) => {
                    self.lock_file = Some(file);
                    self.write_holder()?;
                    return Ok(());
                }
                Err(_) if Instant::now() < deadline => {
                    sleep(backoff);
                    backoff = std::cmp::min(backoff * 2, MAX_BACKOFF);
                }
                Err(_) => {
                    let holder = self.read_holder();
                    return Err(LockError::Timeout { holder });
                }
            }
        }
    }

    pub fn release(&mut self) -> Result<(), LockError> {
        if let Some(ref mut file) = self.lock_file {
            file.set_len(0).ok();
            file.unlock().map_err(LockError::Io)?;
        }
        self.lock_file = None;
        Ok(())
    }

    fn write_holder(&mut self) -> Result<(), LockError> {
        if let Some(ref mut file) = self.lock_file {
            file.set_len(0).map_err(LockError::Io)?;
            file.seek(SeekFrom::Start(0)).map_err(LockError::Io)?;
            write!(
                file,
                "pid:{}\ntime:{}\n",
                std::process::id(),
                chrono::Utc::now().to_rfc3339()
            ).map_err(LockError::Io)?;
            file.sync_all().map_err(LockError::Io)?;
        }
        Ok(())
    }

    fn read_holder(&self) -> String {
        std::fs::read_to_string(&self.lock_path).unwrap_or_else(|_| "unknown".to_string())
    }
}

impl Drop for WriteLocker {
    fn drop(&mut self) {
        self.release().ok();
    }
}
```

## Database Integration

```rust
// db.rs
use rusqlite::{Connection, params};
use std::path::Path;

pub struct Database {
    conn: Connection,
    base_dir: String,
}

impl Database {
    pub fn open(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;
        
        // Enable WAL mode
        conn.execute_batch(
            "PRAGMA journal_mode=WAL;
             PRAGMA busy_timeout=500;
             PRAGMA synchronous=NORMAL;"
        )?;

        let base_dir = Path::new(db_path)
            .parent()
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_else(|| ".".to_string());

        Ok(Self { conn, base_dir })
    }

    fn with_write_lock<T, F>(&self, f: F) -> std::result::Result<T, LockError>
    where
        F: FnOnce(&Connection) -> rusqlite::Result<T>,
    {
        let mut locker = WriteLocker::new(&self.base_dir);
        locker.acquire(DEFAULT_TIMEOUT)?;
        
        let result = f(&self.conn);
        locker.release()?;
        
        result.map_err(|e| LockError::Io(
            std::io::Error::new(std::io::ErrorKind::Other, e.to_string())
        ))
    }

    pub fn create_record(&self, name: &str, value: i32) -> Result<(), LockError> {
        self.with_write_lock(|conn| {
            conn.execute(
                "INSERT INTO records (name, value) VALUES (?1, ?2)",
                params![name, value],
            )?;
            Ok(())
        })
    }
}
```

## Error Formatting

```rust
impl std::fmt::Display for LockError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LockError::Io(e) => write!(f, "lock io error: {}", e),
            LockError::Timeout { holder } => write!(
                f,
                "write lock timeout after 500ms\n  holder: {}\n  try again",
                holder.trim()
            ),
        }
    }
}
```
