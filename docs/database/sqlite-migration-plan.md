# SQLite Migration Plan

## Rationale
CSV backlog is sufficient for early bootstrapping but limits:
- Concurrent safe updates (risk of race conditions)
- Historical query performance and filtering
- Rich relational views (status trends, risk aggregation)
- Idempotent upserts (risk of duplicated external_ref rows)

SQLite provides lightweight, embedded durability aligning with ContextForge event-sourcing:
- Single file, ACID, no service dependency
- Simple promotion path from JSONL + CSV
- Enables indices (external_ref, status, priority_level)
- Supports derived views (e.g., modernization_progress_v)

## Priority
Priority: HIGH (short path, unlocks metrics automation & advanced governance queries). Recommend completion before expanding advanced helper suite.

## Phased Approach
1. Schema Definition (Phase 1): tasks (PK external_ref), task_events, metrics, evidence_index.
2. Loader & Idempotent Upsert: Convert CSV→SQLite; skip existing refs.
3. Dual-Writes (Phase 1-2 overlap): Continue writing CSV for rollback until parity verified.
4. Verification: Row counts match, hash of normalized CSV rows equals SELECT canonical serialization.
5. Promotion: Mark CSV as secondary; update docs & helpers to prefer SQLite.
6. Decommission: Remove CSV writes once 2 consecutive successful verification runs.

## Minimal Schema (v1)

```sql
CREATE TABLE tasks (
  external_ref TEXT PRIMARY KEY,
  priority_level INTEGER,
  priority_section TEXT,
  task_name TEXT,
  description TEXT,
  status TEXT,
  risk_level TEXT,
  created_utc TEXT,
  updated_utc TEXT,
  agent_id TEXT,
  started_utc TEXT,
  completed_utc TEXT
);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority_level);
```

## Migration Script Outline
- Detect presence of `PSSQLite` or fallback to `System.Data.SQLite`.
- Read CSV with `Import-Csv`.
- For each row: UPSERT (INSERT OR IGNORE then UPDATE changed columns if needed).
- Emit `task_db_migration_start/complete` events.

## Verification Steps
1. Count parity: `SELECT COUNT(*) FROM tasks` == CSV row count (excluding header).
2. Hash parity: SHA256 of JSON-sorted projection (external_ref, priority_level, status) matches CSV equivalent.
3. Sample spot checks (first, middle, last rows).

## Parallelization
- Batch insert using transaction blocks of 200 rows.
- Optionally parallel transform of CSV rows into INSERT statements (PS7 ForEach-Object -Parallel) before executing within a single transaction to avoid write contention.

## Rollback Strategy
- Keep original CSV unmodified.
- If verification fails, delete SQLite file and log `task_db_migration_abort`.

## Post-Migration Enhancements
- Add task_history table for status transitions.
- Materialized view for modernization subset (helpers prefix `helper-`).
- Add risk aggregation view (count by risk_level, status).

## Testing Plan (Minimal)
- Unit: Schema creation idempotency (create twice, no error).
- Integration: Migration script run → verify parity steps.
- Governance: Add Pester test ensuring row count parity and hash parity.

## Trigger Integration
Add trigger `MigrateTasksDb` to conversation triggers to invoke migration script when written.

---
Version: 1.0.0
Date: 2025-08-16
