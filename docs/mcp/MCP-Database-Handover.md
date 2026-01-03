# MCP Database Server — Connectivity Handover (Updated v1.0.9 Schema)

Date: 2025-11-13
Scope: Document working PostgreSQL and SQLite connections via MCP database server (@ahmetbarut/mcp-database-server v1.0.9)
Last Updated: 2025-11-13 (Added SQLite schema validation findings)

## Critical Schema Findings (v1.0.9)

**Research Authority**: Official GitHub repository (@ahmetbarut/mcp-database-server)
**Verification Method**: Source code analysis of `src/types/config.ts` and `src/database/drivers/`

### PostgreSQL Configuration Schema
```json
{
  "type": "postgresql",
  "name": "connection-name",
  "host": "hostname",
  "port": 5432,
  "database": "database-name",
  "username": "username",
  "password": "password",
  "maxConnections": 10,
  "timeout": 30000
}
```

**Supported Fields**:
- `type`: `"postgresql"` | `"sqlite"` | `"mysql"` (required)
- `name`: string (required, unique identifier)
- `host`: string (required for PostgreSQL)
- `port`: number (optional, default: 5432)
- `database`: string (required for PostgreSQL)
- `username`: string (required for PostgreSQL)
- `password`: string (required for PostgreSQL)
- `maxConnections`: number (optional, default: 10)
- `timeout`: number (optional, default: 30000ms)

**Unsupported/Ignored Fields**:
- ❌ `ssl` - Not in schema; SSL controlled by `NODE_ENV` environment variable
- ❌ `sslmode` - Not supported
- ❌ Any other fields not listed above

### SQLite Configuration Schema
```json
{
  "type": "sqlite",
  "name": "connection-name",
  "path": "path/to/database.sqlite",
  "maxConnections": 5,
  "timeout": 5000
}
```

**Supported Fields**:
- `type`: `"sqlite"` (required)
- `name`: string (required, unique identifier)
- `path`: string (REQUIRED for SQLite, validated by factory)
- `maxConnections`: number (optional, default: 10, recommend 1-5 for SQLite)
- `timeout`: number (optional, default: 30000ms, maps to busy_timeout)

**Unsupported/Ignored Fields** (Critical Finding):
- ❌ `filename` - Wrong field name; use `path` instead
- ❌ `mode` - Not in schema; better-sqlite3 defaults to read-write
- ❌ `pragmas` - Not supported in v1.0.9 schema
- ❌ Any PRAGMA configuration in JSON

**PRAGMA Workaround**: Execute PRAGMAs manually after connection:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```

## What Changed (Surgical)

### PostgreSQL Configuration
- Adopted file-based config via `.vscode/database-connections.json` (no `ssl` field; schema excludes it)
- Set `NODE_ENV=development` for the database MCP entry in `.vscode/mcp.json` to force non-SSL connections (server does not support SSL)
- Removed unsupported/ignored `ssl` property from the JSON connection definition
- Ensured legacy `POSTGRES_*` env vars don't accidentally create a default "postgres" connection with missing database

### SQLite Configuration (New)
- Added SQLite connection using correct v1.0.9 schema
- **Critical Fix**: Changed `"filename"` to `"path"` (required field name)
- **Removed Unsupported Fields**: `"mode"` and `"pragmas"` (silently ignored by v1.0.9)
- Set `timeout: 5000` which maps to `busy_timeout` in better-sqlite3 driver
- Set `maxConnections: 5` (appropriate for SQLite file-based database)
- PRAGMAs must be set manually via `execute_query` after connection established

## Why This Works
- The package’s Postgres driver sets `ssl: false` unless `NODE_ENV === 'production'`
- The JSON schema for connections does not support `ssl`; SSL is driver-controlled
- `DATABASE_CONNECTIONS_FILE` is the preferred, authoritative configuration source

## Quick Checklist

- VS Code: reload window to restart MCP servers after config changes
	- Command Palette: Developer: Reload Window
- Verify `NODE_ENV=development` is scoped to the database MCP server only
- Confirm `.vscode/database-connections.json` contains no `ssl` property
- List MCP connections: `taskman_v2` should be connected
- Run quick queries: `SELECT 1 AS ping`, `SELECT current_database(), now()`

## How to Validate (Health Checks)

### PostgreSQL Validation
In VS Code with the database MCP enabled:

1) List connections — expect `taskman_v2` to show status: connected
2) List databases on `taskman_v2` — should return real DB names
3) Run health queries:
   - `SELECT 1 AS health_check`
   - `SELECT current_database(), current_user`
   - `SHOW ssl` (expect: 'off' with NODE_ENV=development)
   - `SHOW statement_timeout`

### SQLite Validation
In VS Code with the database MCP enabled:

1) List connections — expect `trackers-sqlite` to show status: connected
2) Run health queries:
   - `PRAGMA integrity_check` (expect: 'ok')
   - `SELECT 1 AS health_check`
   - `PRAGMA database_list` (shows main database file path)
3) Set optimal PRAGMAs (required, not in config):
   - `PRAGMA journal_mode = WAL;` (enables Write-Ahead Logging for concurrency)
   - `PRAGMA synchronous = NORMAL;` (balances safety and performance)
4) Verify PRAGMAs applied:
   - `PRAGMA journal_mode;` (expect: 'wal')
   - `PRAGMA synchronous;` (expect: '1' or 'NORMAL')

**Note**: Unlike PostgreSQL where settings are server-managed, SQLite PRAGMAs must be set per connection after establishing the connection. The v1.0.9 schema does not support PRAGMA configuration in the JSON file.

### Direct SQL Validation (Optional)
If you prefer validation outside MCP:

```powershell
# PostgreSQL (no SSL)
psql -h 172.25.14.122 -p 5432 -U contextforge -d taskman_v2 -c "SELECT current_database(), now();"

# SQLite (using sqlite3 CLI)
sqlite3 db/trackers.sqlite "PRAGMA integrity_check; SELECT 1 AS health_check;"
```

## Rollback / Undo
- If you must switch to production for other servers, keep the database MCP `NODE_ENV` at `development` unless Postgres adds SSL support
- Alternatively, enable SSL on the Postgres server and then you may set `NODE_ENV=production`
- If legacy envs are needed: use `POSTGRES_*` consistently (host, port, database, username, password) and remove file-based entry to avoid conflicts

Environment scoping tip: In `.vscode/mcp.json`, scope `NODE_ENV=development` only for the database MCP server block so other servers can keep their preferred values.

## Troubleshooting & Runbook

### PostgreSQL Errors

**Error: The server does not support SSL connections**
- Cause: Driver SSL enabled (typically `NODE_ENV=production`)
- Fix: Set `NODE_ENV=development` for the database MCP or enable SSL on Postgres

**Error: Database name is required for postgresql database**
- Cause: Legacy `POSTGRES_*` envs without `POSTGRES_DB`
- Fix: Add the `database` field in file-based config or set `POSTGRES_DB`; prefer `DATABASE_CONNECTIONS_FILE`

**Error: no pg_hba.conf entry for host/user/database**
- Cause: Server access not granted for client IP/user/db
- Fix: Update `pg_hba.conf` to allow the client CIDR for the specified user/db; reload/restart Postgres

**Error: ECONNREFUSED / timeout**
- Cause: Host/port unreachable, firewall, or incorrect IP
- Fix: Verify IP/port, security group/firewall rules; test with `Test-NetConnection 172.25.14.122 -Port 5432`

**Error: password authentication failed / permission denied**
- Cause: Wrong credentials or insufficient privileges
- Fix: Verify `username/password`; confirm role can connect to `taskman_v2`

**Warning: ssl property in JSON is ignored**
- Cause: Schema excludes `ssl`; driver handles SSL via environment
- Fix: Remove `ssl` from `.vscode/database-connections.json`

### SQLite Errors

**Error: Path is required for SQLite database**
- Cause: Missing `path` field or using wrong field name (`filename`)
- Fix: Use `"path": "db/trackers.sqlite"` (not `"filename"`)

**Error: SQLITE_CANTOPEN / unable to open database file**
- Cause: File doesn't exist, wrong path, or permission denied
- Fix:
  1. Verify file exists: `Test-Path "db/trackers.sqlite"`
  2. Check path is relative to workspace root
  3. Check file permissions: `icacls "db\trackers.sqlite"`

**Error: Database is locked**
- Cause: Another process has exclusive lock
- Fix:
  1. Close other applications accessing the database
  2. Check for `.sqlite-journal` or `.sqlite-shm` lock files
  3. Set `PRAGMA journal_mode = WAL;` for better concurrency

**Warning: pragmas/mode fields in JSON are ignored**
- Cause: v1.0.9 schema does not support these fields
- Fix: Remove from JSON config; set PRAGMAs manually via `execute_query` after connection

### General Errors

**After edits, connection still shows failed**
- Action: Reload VS Code window to restart MCP servers (Developer: Reload Window); wait ~10–15 seconds and re-run validation

## Risks & Gotchas

### PostgreSQL
- Flipping `NODE_ENV` to `production` re-enables SSL in the driver and will fail against non-SSL Postgres with: "The server does not support SSL connections"
- Adding `ssl` in `.vscode/database-connections.json` has no effect and is out-of-schema
- Stray `POSTGRES_*` envs can create a phantom default connection named `postgres` without a database

### SQLite (Critical Findings)
- **Field Name Matters**: Must use `"path"` not `"filename"` (will fail with "Path is required" error)
- **No PRAGMA Support in JSON**: v1.0.9 schema does NOT support `"pragmas"` or `"mode"` fields
  - These fields are silently ignored if present
  - Must set PRAGMAs manually after connection via `execute_query`
- **Timeout Mapping**: `"timeout"` in JSON maps to `busy_timeout` in better-sqlite3 (not connection timeout)
- **Connection Pooling**: SQLite file-based DBs benefit from lower `maxConnections` (1-5) vs PostgreSQL (10+)
- **Foreign Keys**: Hardcoded to `ON` by driver (cannot be changed via config)
- **In-Memory Fallback**: If `path` is missing, driver defaults to `:memory:` (temporary database)

## References (Source-Verified)

### Schema Documentation (v1.0.9)
- **PostgreSQL**: `type, name, host, port, database, username, password, maxConnections, timeout`
- **SQLite**: `type, name, path (required), maxConnections, timeout`
- **Unsupported Fields**: `ssl, sslmode, filename, mode, pragmas` (not in Zod schema)
- **Source**: `src/types/config.ts` (DatabaseConfigSchema definition)

### Driver Implementation
- **PostgreSQL Driver** (`src/database/drivers/postgres-driver.ts`):
  - SSL controlled by `NODE_ENV` (production = SSL, development = no SSL)
  - Executes `SELECT 1` health check on connect
- **SQLite Driver** (`src/database/drivers/sqlite-driver.ts`):
  - Uses better-sqlite3 library
  - Hardcodes `PRAGMA foreign_keys = ON`
  - `timeout` parameter maps to better-sqlite3 busy_timeout
  - Path defaults to `:memory:` if not provided

### Configuration Priority
- Settings loader prioritizes `DATABASE_CONNECTIONS_FILE`
- Legacy `POSTGRES_*` environment variables supported for single-connection mode
- File-based config is authoritative when present

### Research Sources
- Official Repository: github.com/ahmetbarut/mcp-database-server
- Version Validated: v1.0.9
- Files Analyzed: `src/types/config.ts`, `src/database/factory.ts`, `src/database/drivers/`
- Research Date: 2025-11-13

## Maintenance Notes
- Keep `.vscode/mcp.json` and `.vscode/database-connections.json` in sync
- Prefer minimal, reversible changes; avoid committing secrets
- If other MCP servers require `NODE_ENV=production`, scope the env only for those servers and leave the database MCP on `development`
