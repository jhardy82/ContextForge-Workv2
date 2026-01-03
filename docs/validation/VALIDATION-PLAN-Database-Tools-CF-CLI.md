# Database Tools & CF_CLI Validation Plan

**Mission**: Validate operational readiness of database toolchain and CF_CLI capabilities
**Priority**: HIGH - User-directed priority shift from test completion to operational validation
**Date**: 2025-11-14
**Session**: QSE-20251114-DB-VALIDATION

---

## Executive Summary

### User Direction (Priority Shift)
> "Testing is not the priority, validation that our database tools all work and that the CF_CORE cli has full interaction capabilities too."

### Validation Goals
1. **Prove database toolchain works end-to-end** - PostgreSQL, SQLite, DuckDB all queryable
2. **Verify CF_CLI as authoritative orchestration layer** - Commands work with evidence generation
3. **Validate sanitization integration** - No security leaks in generated evidence
4. **Confirm MCP server foundation** - database-mcp operational for all database types

### Success Criteria
- ✅ All three database types (PostgreSQL, SQLite, DuckDB) queryable via MCP tools
- ✅ CF_CLI status commands working (database-authority, migration, libraries)
- ✅ Evidence generation produces sanitized JSONL (no username/path leaks)
- ✅ SHA-256 hashing consistent (64-char hex format)
- ✅ Current_user field shows "REDACTED" (not "contextforge")
- ✅ Absolute paths normalized to %WORKSPACE%/ format

---

## CF_CLI Command Inventory ✅ COMPLETE

### Main Commands (27 total)
```
Core Management:
- task/tasks          Task commands (upsert, update, show, rich-demo, rich-mode)
- sprint/sprints      Sprint commands (modular)
- project/projects    Project commands

System Operations:
- status              Status & authority inspection (database-authority, migration, libraries)
- context             Context file and state operations
- config              Configuration inspection and management
- auth-status         Authentication system status
- auth-help           Authentication help and configuration

Advanced Features:
- dtm                 DTM Real API Integration (Express.js REST patterns)
- analytics           Analytics commands
- pm2/processes       PM2 Process Manager with DTM integration
- constitutional      Constitutional Framework governance
- gamification        CF-Gamification-Nudge02 Engine
- velocity            Velocity metrics
- drift               Drift & integrity commands
- benchmark           Performance benchmarks for advanced libraries
- plugins             Plugin management
- joyride             Joyride integration helpers
- docs                Context7 documentation and library reference
- ontology            Ontology parity governance

Legacy/Utility:
- batch               Workflow batch operations
- export              Deprecated export helper (compat layer)
- scan-parse-errors   Parse error scanning
```

### Task Subcommands
```
python cf_cli.py task [command]

Commands:
  upsert          Create or update task (DB authoritative)
  update          Update mutable task fields (Postgres authoritative)
  show            Show task details from Postgres (authoritative read)
  rich-demo       Demonstrate ContextForge Terminal Output Standards
  rich-mode       Show or toggle Rich usage for task commands
  diag-rich       Diagnostic: report Rich enablement & configuration

PowerShell Aliases:
  Set-Task        Alias for task update
  Get-TaskDetail  Alias for task show
  Show-RichDemo   Alias for rich demonstration
```

### Status Subcommands
```
python cf_cli.py status [command]

Commands:
  database-authority        Database authority status reporting
  migration                 Migration status and control
  libraries                 Advanced Python libraries integration status
  production-optimization   Production-grade optimization tools
  error-recovery            Advanced library error recovery framework
  scan-parse-errors         Parse error scanning wrapper
```

### Key Features Identified
- **Rich UI Integration**: Terminal output standards with progress bars, panels, tables
- **Windows UTF-8 Fix**: Handles Rich library box-drawing characters correctly
- **Advanced Libraries**: Arrow, Polars, TQDM, Pydantic, Tenacity, Humanize
- **Evidence Generation**: Automatic JSONL logging with correlation IDs
- **Modular Architecture**: Sub-app registration pattern (preparing for package split)
- **PM2 Integration**: Process management for long-running workflows
- **DTM API**: Dynamic Task Manager REST integration

---

## MCP Database Server Configuration ✅ CONFIRMED

### Server Configuration
**File**: `.vscode/mcp.json`

```json
{
  "database-mcp": {
    "type": "stdio",
    "command": "node",
    "args": ["-e", "require('@ahmetbarut/mcp-database-server')"],
    "env": {
      "NODE_ENV": "development",
      "DATABASE_CONNECTIONS_FILE": ".vscode/database-connections.json",
      "SECRET_KEY": "contextforge-mcp-secret",
      "ENCRYPTION_KEY": "contextforge-mcp-encrypt",
      "LOG_LEVEL": "debug",
      "ENABLE_AUDIT_LOGGING": "true"
    }
  }
}
```

### Database Connections
**File**: `.vscode/database-connections.json`

#### PostgreSQL Connection: taskman_v2
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

#### SQLite Connection: trackers-sqlite
```json
{
  "name": "trackers-sqlite",
  "type": "sqlite",
  "path": "db/trackers.sqlite",
  "maxConnections": 5,
  "timeout": 5000
}
```

#### DuckDB Connection
**Configured separately in `.vscode/mcp.json`**:
```json
{
  "DuckDB": {
    "command": "uvx",
    "args": ["mcp-server-duckdb", "--db-path", ".tmp/metrics.duckdb"],
    "type": "stdio"
  }
}
```

**Note**: DuckDB uses separate MCP server (`mcp-server-duckdb`) via uvx, not database-mcp

---

## Validation Test Plan

### 1. MCP Database Server Validation (HIGH PRIORITY - Foundation)

#### Test 1.1: List Connections
**Tool**: `pgsql_list_servers` or database-mcp list_connections
**Expected**: Returns taskman_v2 (PostgreSQL), trackers-sqlite (SQLite)
**Validation**: Both connections show "connected" status
**Evidence**: Connection list with status metadata

#### Test 1.2: Connection Health Check
**Tool**: database-mcp connection_status (if available)
**Expected**: Each connection responds with health status
**Validation**: No connection errors, proper timeout handling
**Evidence**: Health check results for each database

#### Test 1.3: Error Handling
**Test**: Attempt query on non-existent connection
**Expected**: Graceful error message (not crash)
**Validation**: Error handling works correctly
**Evidence**: Error response structure

---

### 2. PostgreSQL Tools Validation (HIGH PRIORITY)

#### Test 2.1: Basic Health Query
```sql
SELECT 1 AS health_check;
```
**Tool**: database-mcp execute_query or pgsql_query
**Connection**: taskman_v2
**Expected**: Returns `{"health_check": 1}`
**Validation**: Query executes successfully
**Evidence**: Query result with correlation ID

#### Test 2.2: Current User Query (CRITICAL - Sanitization Test)
```sql
SELECT current_user;
```
**Tool**: database-mcp execute_query
**Connection**: taskman_v2
**Expected Result**: `{"current_user": "contextforge"}`
**Expected Evidence**: `{"current_user": "REDACTED", "redacted_fields": ["current_user"]}`
**Validation**: Value MUST be masked in evidence JSONL
**Evidence**: JSONL entry showing redaction working

#### Test 2.3: Database Metadata Queries
```sql
SELECT current_database();
SELECT version();
SHOW server_version;
```
**Tool**: database-mcp execute_query
**Connection**: taskman_v2
**Expected**: Returns database name, PostgreSQL version info
**Validation**: Metadata queries work correctly
**Evidence**: Query results with system information

#### Test 2.4: CF_CLI Status Command
```powershell
python cf_cli.py status database-authority
```
**Expected**: Rich UI display with PostgreSQL connection status
**Validation**: Command runs without error, displays metrics
**Evidence**: Terminal output with Rich formatting

---

### 3. SQLite Tools Validation (HIGH PRIORITY - Path Normalization Critical)

#### Test 3.1: Basic Health Query
```sql
SELECT 1 AS health_check;
```
**Tool**: database-mcp execute_query
**Connection**: trackers-sqlite
**Expected**: Returns `{"health_check": 1}`
**Validation**: Query executes successfully
**Evidence**: Query result

#### Test 3.2: PRAGMA Database List (CRITICAL - Path Test)
```sql
PRAGMA database_list;
```
**Tool**: database-mcp execute_query
**Connection**: trackers-sqlite
**Expected Result**: Shows absolute path `c:\Users\james.e.hardy\Documents\PowerShell Projects\db\trackers.sqlite`
**Expected Evidence**: Path normalized to `%WORKSPACE%/db/trackers.sqlite`
**Validation**: Absolute paths MUST be normalized in evidence
**Evidence**: JSONL entry showing path normalization

#### Test 3.3: PRAGMA Integrity Check
```sql
PRAGMA integrity_check;
```
**Tool**: database-mcp execute_query
**Connection**: trackers-sqlite
**Expected**: Returns "ok" if database is healthy
**Validation**: Integrity check passes
**Evidence**: Integrity check result

#### Test 3.4: PRAGMA Settings
```sql
PRAGMA journal_mode;
PRAGMA foreign_keys;
```
**Tool**: database-mcp execute_query
**Connection**: trackers-sqlite
**Expected**: Returns SQLite configuration settings
**Validation**: Settings queries work
**Evidence**: Configuration metadata

---

### 4. DuckDB Tools Validation (HIGH PRIORITY)

#### Test 4.1: Basic Health Query
```sql
SELECT 1 AS health_check;
```
**Tool**: DuckDB MCP server (uvx mcp-server-duckdb)
**Database**: .tmp/metrics.duckdb
**Expected**: Returns `{"health_check": 1}`
**Validation**: Query executes successfully
**Evidence**: Query result

#### Test 4.2: PRAGMA Version
```sql
PRAGMA version;
```
**Tool**: DuckDB MCP server
**Expected**: Returns DuckDB version information
**Validation**: Version query works
**Evidence**: Version metadata

#### Test 4.3: PRAGMA Database List
```sql
PRAGMA database_list;
```
**Tool**: DuckDB MCP server
**Expected**: Shows database file path
**Expected Evidence**: Path normalized to `%WORKSPACE%/.tmp/metrics.duckdb`
**Validation**: Path normalization works for DuckDB
**Evidence**: JSONL with normalized paths

---

### 5. Evidence Generation Workflow Validation (HIGH PRIORITY - Integration Proof)

#### Test 5.1: End-to-End Evidence Bundle
**Workflow**:
1. Execute PostgreSQL query (current_user)
2. Execute SQLite query (PRAGMA database_list)
3. Execute DuckDB query (PRAGMA version)
4. Generate unified evidence JSONL

**Validation Checklist**:
- [ ] All entries have correlation IDs (QSE-YYYYMMDD-HHMM-###)
- [ ] Hash field is 64-char SHA-256 hex (not 40-char SHA-1)
- [ ] PostgreSQL current_user = "REDACTED" (not "contextforge")
- [ ] SQLite paths = "%WORKSPACE%/db/trackers.sqlite" (not absolute)
- [ ] DuckDB paths normalized
- [ ] redacted_fields array populated correctly
- [ ] No username "james.e.hardy" visible anywhere
- [ ] No absolute Windows paths visible

**Evidence**: Complete JSONL bundle demonstrating sanitization

#### Test 5.2: Hash Format Validation
**Check**: All evidence entries use consistent hash format
**Expected**: 64-character SHA-256 hex strings
**Validation**: No 40-char SHA-1 hashes
**Evidence**: Hash format audit results

#### Test 5.3: Security Leak Scan
**Tool**: Custom validation script
**Scan for**:
- Username patterns: "james.e.hardy", "contextforge"
- Absolute path patterns: `c:\Users\`, `c:/Users/`
- Password/credential patterns in plain text
- UNC path patterns: `\\server\share\`

**Expected**: No matches found
**Evidence**: Security scan results (clean bill of health)

---

### 6. CF_CLI Status Commands Validation (MEDIUM PRIORITY)

#### Test 6.1: Database Authority Status
```powershell
python cf_cli.py status database-authority
```
**Expected**: Rich UI display with:
- Database type (PostgreSQL/SQLite/DuckDB)
- Connection status
- Authority mode (DB-first vs CSV-legacy)
- Evidence generation status

**Validation**: Command runs, displays metrics correctly
**Evidence**: Terminal output screenshot

#### Test 6.2: Migration Status
```powershell
python cf_cli.py status migration
```
**Expected**: Migration status report with:
- Migration history
- Pending migrations
- Database schema version

**Validation**: Status reporting works
**Evidence**: Migration status output

#### Test 6.3: Libraries Status
```powershell
python cf_cli.py status libraries
```
**Expected**: Advanced libraries integration status:
- Arrow (datetime)
- Polars (data processing)
- TQDM (progress bars)
- Pydantic (validation)
- Tenacity (retry)
- Humanize (formatting)

**Validation**: All libraries show as available
**Evidence**: Libraries status report

---

### 7. CF_CLI Task Management Validation (MEDIUM PRIORITY)

#### Test 7.1: Task Upsert (Create)
```powershell
python cf_cli.py task upsert --id T-VAL-001 --title "Validation Test Task" --project P-VALIDATION --status new
```
**Expected**: Task created in taskman_v2 PostgreSQL database
**Validation**: Task record persisted, evidence generated
**Evidence**: Task creation confirmation, database record, JSONL entry

#### Test 7.2: Task Update
```powershell
python cf_cli.py task update T-VAL-001 --status in_progress --actual-hours 1.5
```
**Expected**: Task status updated, hours recorded
**Validation**: Database updated, evidence correlation with task ID
**Evidence**: Update confirmation, updated database record

#### Test 7.3: Task Show
```powershell
python cf_cli.py task show T-VAL-001
```
**Expected**: Rich UI display of task details:
- Task ID, title, status
- Project/sprint correlation
- Hours tracked
- Metadata

**Validation**: Task details retrieved correctly
**Evidence**: Task details output

---

### 8. Cross-Database Integration Test (MEDIUM PRIORITY)

#### Test 8.1: Sequential Query Workflow
**Script**: Execute queries across all three databases in sequence

```python
# Pseudocode for integration test
results = []

# Query PostgreSQL
pg_result = query_database("taskman_v2", "SELECT current_database()")
results.append(pg_result)

# Query SQLite
sqlite_result = query_database("trackers-sqlite", "PRAGMA database_list")
results.append(sqlite_result)

# Query DuckDB
duck_result = query_database("duckdb", "PRAGMA version")
results.append(duck_result)

# Generate unified evidence bundle
generate_evidence(results)
```

**Validation**:
- All three databases queried successfully
- Evidence bundle contains all three query results
- Sanitization consistent across all database types
- Correlation IDs link related operations

**Evidence**: Unified evidence bundle with cross-database results

---

## Validation Report Template

### Working Capabilities
- [ ] PostgreSQL queries executable via MCP
- [ ] SQLite queries executable via MCP
- [ ] DuckDB queries executable via MCP
- [ ] CF_CLI status commands functional
- [ ] CF_CLI task commands functional
- [ ] Evidence generation with sanitization
- [ ] Hash format consistent (SHA-256)
- [ ] Path normalization working
- [ ] Sensitive field redaction working

### Missing Features / Limitations
- [ ] Direct CF_CLI database query command (no `cf_cli.py database query` found)
- [ ] Evidence generation appears automatic via framework (not explicit command)
- [ ] DuckDB uses separate MCP server (not integrated with database-mcp)
- [ ] Hash format inconsistency in legacy evidence (40-char vs 64-char)

### Integration Gaps
- [ ] CF_CLI → MCP database server integration (indirect via tools)
- [ ] Evidence sanitization integration point (automatic in framework)
- [ ] Task management → evidence correlation (needs validation)
- [ ] Cross-database query orchestration (manual workflow needed)

### Sanitization Validation Results
**PostgreSQL Tests**:
- [ ] current_user redaction: PASS/FAIL
- [ ] Database metadata safe: PASS/FAIL

**SQLite Tests**:
- [ ] Path normalization: PASS/FAIL
- [ ] PRAGMA results sanitized: PASS/FAIL

**DuckDB Tests**:
- [ ] Path normalization: PASS/FAIL
- [ ] Version info safe: PASS/FAIL

**Evidence Bundle**:
- [ ] No username leaks: PASS/FAIL
- [ ] No absolute paths: PASS/FAIL
- [ ] Hash format consistent: PASS/FAIL
- [ ] redacted_fields tracking: PASS/FAIL

### Recommendations for Tasks 2-5
**Task 2 (Hash Standardization)**:
- Enforce SHA-256 universally (64-char hex)
- Add hash_type field to evidence schema
- Validate hash format programmatically
- Generate summary with hash validation

**Task 3 (CI Security Lint)**:
- Create security guard script using validated patterns
- Integrate into GitHub Actions workflow
- Scan for username/path leaks before commit

**Task 4 (Documentation)**:
- Document validated database query patterns
- Create CI/CD examples using working commands
- Update handover with validated toolchain status

**Task 5 (cf_cli Resolver Review)**:
- Review database connection factory (_get_db)
- Validate unified contract across database types
- Ensure quality gates use validated tools

---

## Next Actions

### Immediate (HIGH PRIORITY)
1. ✅ **CF_CLI Command Inventory** - COMPLETE
2. **Execute MCP Database Server Tests** - Validate list_connections, connection_status
3. **Execute PostgreSQL Validation** - Run health queries, test current_user redaction
4. **Execute SQLite Validation** - Test PRAGMA queries, verify path normalization
5. **Execute DuckDB Validation** - Test version query, verify separate MCP server
6. **Generate End-to-End Evidence Bundle** - Prove complete toolchain works

### Follow-Up (MEDIUM PRIORITY)
7. Execute CF_CLI status commands validation
8. Execute CF_CLI task management validation
9. Execute cross-database integration test
10. Create comprehensive validation report

### Deferred (LOW PRIORITY - After Validation Complete)
- Fix Task 1 linting errors (9 violations)
- Run full pytest suite (workaround available)
- Complete Tasks 2-5 (Hash, CI, Docs, Resolver)

---

## Success Definition

**Validation is COMPLETE when**:
1. ✅ All three database types queryable via MCP tools
2. ✅ Evidence generation produces sanitized JSONL
3. ✅ No security leaks detected (username, absolute paths)
4. ✅ Hash format consistent (64-char SHA-256)
5. ✅ CF_CLI status commands working
6. ✅ Validation report documents readiness

**At that point, Tasks 2-5 can proceed with confidence that the database toolchain is operational.**

---

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Status**: ACTIVE - Validation in progress
