# MCP Database Server Schema Reference (v1.0.9)

**Package**: @ahmetbarut/mcp-database-server
**Version**: v1.0.9
**Research Date**: 2025-11-13
**Authority**: Official GitHub repository source code analysis

---

## Schema Definition (Zod)

```typescript
export const DatabaseConfigSchema = z.object({
  type: z.enum(['sqlite', 'postgresql', 'mysql']),
  name: z.string(),
  path: z.string().optional(),          // SQLite-specific
  host: z.string().optional(),          // Network DB specific
  port: z.number().optional(),
  database: z.string().optional(),
  username: z.string().optional(),
  password: z.string().optional(),
  maxConnections: z.number().default(10),
  timeout: z.number().default(30000)
});
```

**Source**: `src/types/config.ts` (Lines 6-19)

---

## PostgreSQL Configuration

### Required Fields
- `type`: `"postgresql"` (literal string)
- `name`: string (unique connection identifier)
- `host`: string (hostname or IP address)
- `database`: string (database name)
- `username`: string (database user)
- `password`: string (user password)

### Optional Fields
- `port`: number (default: 5432)
- `maxConnections`: number (default: 10)
- `timeout`: number (milliseconds, default: 30000)

### Example Configuration
```json
{
  "name": "taskman_v2",
  "type": "postgresql",
  "host": "172.25.14.122",
  "port": 5432,
  "database": "taskman_v2",
  "username": "contextforge",
  "password": "contextforge",
  "maxConnections": 10,
  "timeout": 30000
}
```

### SSL Configuration
**Critical**: SSL is NOT configurable via JSON schema in v1.0.9.

**SSL Control**: Determined by `NODE_ENV` environment variable in `.vscode/mcp.json`:
- `NODE_ENV=production` → SSL enabled (pg driver default)
- `NODE_ENV=development` → SSL disabled

**Source**: `src/database/drivers/postgres-driver.ts` (Lines 20-35)

### Unsupported Fields (Silently Ignored)
- ❌ `ssl` (boolean or object) - Not in schema
- ❌ `sslmode` - Not in schema
- ❌ Any other fields not listed above

---

## SQLite Configuration

### Required Fields
- `type`: `"sqlite"` (literal string)
- `name`: string (unique connection identifier)
- `path`: string (REQUIRED despite being optional in Zod schema)
  - **Factory Validation** enforces this as required
  - **Error if missing**: "Path is required for SQLite database"

### Optional Fields
- `maxConnections`: number (default: 10, recommend 1-5 for file-based SQLite)
- `timeout`: number (milliseconds, default: 30000, maps to busy_timeout)

### Example Configuration
```json
{
  "name": "trackers-sqlite",
  "type": "sqlite",
  "path": "db/trackers.sqlite",
  "maxConnections": 5,
  "timeout": 5000
}
```

### Path Resolution
- Relative paths resolved from `process.cwd()` (workspace root)
- Absolute paths supported
- Special value `:memory:` creates in-memory database (not recommended for production)

**Fallback Behavior**: If `path` is not provided (fails validation), driver defaults to `:memory:`

**Source**: `src/database/drivers/sqlite-driver.ts` (Lines 14-46)

### Unsupported Fields (Silently Ignored)
- ❌ `filename` - Wrong field name; use `path` instead
- ❌ `mode` - Not in schema; better-sqlite3 defaults to read-write
- ❌ `pragmas` - Not in schema (v1.0.9)
- ❌ Any PRAGMA configuration in JSON

### PRAGMA Configuration Workaround

**Problem**: v1.0.9 schema does NOT support PRAGMA configuration in JSON.

**Solution**: Execute PRAGMAs manually after connection via `execute_query`:

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;
```

**Hardcoded PRAGMAs** (Applied by driver):
- `PRAGMA foreign_keys = ON` (always enabled, cannot be disabled)

**Timeout Mapping**:
- JSON `timeout` parameter maps to better-sqlite3 `timeout` option
- better-sqlite3 `timeout` maps to SQLite `busy_timeout` PRAGMA
- Result: JSON `timeout: 5000` → SQLite `PRAGMA busy_timeout = 5000`

**Recommended PRAGMAs for Production**:
```sql
PRAGMA journal_mode = WAL;        -- Better concurrency
PRAGMA synchronous = NORMAL;      -- Balance safety/performance
PRAGMA busy_timeout = 5000;       -- Set via JSON timeout field
PRAGMA foreign_keys = ON;         -- Already enabled by driver
```

**Source**: `src/database/drivers/sqlite-driver.ts` (Lines 28-46)

---

## Common Validation Errors

### PostgreSQL Errors

**"Database name is required for postgresql database"**
- **Cause**: Missing `database` field in JSON or `POSTGRES_DB` env var
- **Fix**: Add `"database": "your_database_name"` to JSON config

**"The server does not support SSL connections"**
- **Cause**: `NODE_ENV=production` enables SSL, but server has SSL disabled
- **Fix**: Set `NODE_ENV=development` in `.vscode/mcp.json` for database MCP server

### SQLite Errors

**"Path is required for SQLite database"**
- **Cause**: Missing `path` field or using wrong field name (`filename`)
- **Fix**: Use `"path": "db/your-database.sqlite"`

**SQLITE_CANTOPEN / "unable to open database file"**
- **Cause**: File doesn't exist, wrong path, or permission denied
- **Fix**:
  1. Verify file exists: `Test-Path "db/your-database.sqlite"`
  2. Ensure path is relative to workspace root
  3. Check file permissions

---

## Configuration File Location

**File**: `.vscode/database-connections.json`

**Environment Variable**: `DATABASE_CONNECTIONS_FILE`
- Set in `.vscode/mcp.json` under database MCP server `env` section
- Must point to absolute path or path relative to MCP server working directory

**Example `.vscode/mcp.json` Configuration**:
```json
{
  "mcpServers": {
    "database-mcp": {
      "command": "npx",
      "args": ["-y", "@ahmetbarut/mcp-database-server"],
      "env": {
        "DATABASE_CONNECTIONS_FILE": "${workspaceFolder}/.vscode/database-connections.json",
        "NODE_ENV": "development"
      }
    }
  }
}
```

---

## Legacy Environment Variable Support

### PostgreSQL Single-Connection Mode
If `DATABASE_CONNECTIONS_FILE` is not set, the server falls back to discrete environment variables:

```bash
POSTGRES_HOST=172.25.14.122
POSTGRES_PORT=5432
POSTGRES_DB=taskman_v2
POSTGRES_USER=contextforge
POSTGRES_PASSWORD=contextforge
```

**Gotcha**: Missing `POSTGRES_DB` creates a phantom connection named `postgres` with no database, which will fail.

**Recommendation**: Use file-based configuration (`DATABASE_CONNECTIONS_FILE`) as primary method.

---

## Driver Implementation Notes

### PostgreSQL Driver
- **Library**: `pg` (node-postgres)
- **Health Check**: Executes `SELECT 1` on connection
- **SSL**: Controlled by `NODE_ENV`, not JSON config
- **Connection Pooling**: Uses pg Pool with maxConnections parameter

**Source**: `src/database/drivers/postgres-driver.ts`

### SQLite Driver
- **Library**: `better-sqlite3`
- **Mode**: Always read-write (not configurable in v1.0.9)
- **Foreign Keys**: Hardcoded to `ON`
- **Timeout**: JSON `timeout` maps to better-sqlite3 busy timeout
- **In-Memory Fallback**: Uses `:memory:` if path validation fails

**Source**: `src/database/drivers/sqlite-driver.ts`

---

## Version History

### v1.0.9 (Current)
- PostgreSQL and SQLite support
- File-based configuration via `DATABASE_CONNECTIONS_FILE`
- No PRAGMA configuration support for SQLite
- SSL controlled by `NODE_ENV` for PostgreSQL

### Future Versions
**Potential Enhancements** (not in v1.0.9):
- PRAGMA configuration in JSON schema
- SQLite mode configuration (read-only, read-write)
- SSL configuration options in JSON
- Connection string format support

---

## Research Methodology

**Primary Sources**:
1. Official GitHub Repository: github.com/ahmetbarut/mcp-database-server
2. Package Version: v1.0.9 (verified via `node_modules/` inspection)
3. Source Files Analyzed:
   - `src/types/config.ts` (Zod schema definition)
   - `src/database/factory.ts` (validation logic)
   - `src/database/drivers/postgres-driver.ts` (PostgreSQL implementation)
   - `src/database/drivers/sqlite-driver.ts` (SQLite implementation)
4. Test Files Reviewed:
   - `tests/unit/config/settings.test.ts`
   - `examples/configuration-examples/json-connections.js`

**Verification Method**: Direct source code analysis + subagent research validation

**Last Verified**: 2025-11-13

---

## Related Documentation

- [MCP Database Handover](./MCP-Database-Handover.md) - Connection setup guide
- [PostgreSQL Smoke Tests Report](./PostgreSQL-Smoke-Tests-Validation-Report.md) - Test results
- [SQLite Validation Guide](./SQLite-Validation-Next-Steps.md) - SQLite setup steps

---

**Document Authority**: Source-verified schema reference
**Maintenance**: Update when upgrading @ahmetbarut/mcp-database-server version
**Status**: Complete and validated for v1.0.9
