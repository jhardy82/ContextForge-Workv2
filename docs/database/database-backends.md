# Database Backends (SQLite + MSSQL)

This document outlines the dual‑backend approach for tracker storage.

## Selection
Backend is chosen via environment variable `CF_DB` (`sqlite` default, `mssql` optional). Optional variables:
- `CF_MSSQL_PROFILE` profile name / connection hint (future integration)
- `CF_DB_SCHEMA` schema name for MSSQL (default `dbo`)

`tools/Select-DbBackend.ps1` returns an object: `{ backend, profile, schema }`.

## Migrations
Migrations live under `migrations/` with dialect suffix:
- `0001_init.sqlite.sql` / `0001_init.mssql.sql`
- `0002_rbac.sqlite.sql` / `0002_rbac.mssql.sql`

Apply with: `pwsh ./tools/Invoke-Migrations.ps1`

SQLite migrations are executed directly via `System.Data.SQLite`; MSSQL path currently logs intent (placeholder until profile execution implemented).

## Data Access Layer
Module: `modules/TrackerDal/TrackerDal.psm1`
Exports:
- `Get-DbBackendSelection`
- `Open-DbConnection` (sqlite now, mssql placeholder)
- `Write-TaskAuditRecord` (sqlite implementation)

## Roadmap
1. Implement MSSQL execution (Invoke-Sqlcmd or extension API)
2. Expand DAL with CRUD functions (Get-Task, Upsert-Task, List-Tasks, Get-Project)
3. Introduce RBAC enforcement layer mapping roles -> permitted operations
4. Health checks: orphan FK scan, schema drift vs `schema/trackers.model.json`, row counts, fragmentation (MSSQL), trigger validity
5. Drift detection script and Pester parity tests across backends

## RBAC (Initial)
Migration `0002_rbac.*.sql` introduces `role` and `role_grant` tables. Enforcement not yet wired.

## Audit
Both dialects create `task_audit` + triggers (MSSQL) or triggers (SQLite). `Write-TaskAuditRecord` allows manual insertion for scripted actions.

## Versioning
`schema_versions` captures applied migrations and checksum placeholder. Future enhancement: compute SHA256 of migration file content at application time.

## Testing Strategy (Planned)
Pester suite will:
1. Run migrations (sqlite) and validate tables match model JSON
2. Insert sample task; verify audit row
3. Simulate update; verify audit delta
4. (Future) MSSQL simulation or conditional skip when backend not available

## Compliance Tags
HostPolicy: ModernPS7
Shapes: Triangle (foundation) progressing to Circle (integration) once MSSQL path implemented.
