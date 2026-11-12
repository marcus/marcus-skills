# Storage

Start with the simplest store that works and let real pressure, not anticipation, drive the upgrade. The usual progression is **JSONL → SQLite → Postgres**.

Start at JSONL: inspectable, diffable, greppable, repairable by an agent with ordinary tools, and trivially version-controlled. Move up only when concrete pain appears (concurrent writers, query complexity, data volume, multi-host access), and say what the pain was.

What makes that progression cheap is the **interface**, so keep it clean from day one:

- All persistence goes through one narrow store/repository interface. No file paths, SQL, or driver types leak into callers.
- **Avoid store-specific features.** No SQLite-only pragmas, no Postgres-only types or extensions, no clever JSONL-layout tricks in business logic. Anything you can't express against a plain key/record/query interface is a future migration tax.
- Assume the destination may not be a SQL database at all. More agentic data stores are coming; the interface should survive one of those becoming the right choice.
- Migrations are an adapter concern, not an app concern.
