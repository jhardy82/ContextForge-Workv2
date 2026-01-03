# DTM to TaskMan-v2 MCP Migration Guide

**Version**: 1.0.0
**Created**: 2025-11-16
**Authority**: ContextForge Work | TaskMan-v2 MCP Architecture
**Status**: Production Guidance

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Changes](#architecture-changes)
3. [Command Mapping](#command-mapping)
4. [Environment Setup](#environment-setup)
5. [VS Code Integration](#vs-code-integration)
6. [Troubleshooting](#troubleshooting)
7. [Rollback Procedures](#rollback-procedures)

---

## Overview

### Migration Rationale

The Dynamic Task Manager (DTM) has been superseded by **TaskMan-v2 MCP Server** to provide:

- **Unified Protocol**: Model Context Protocol (MCP) standardization across all task management operations
- **Enhanced Reliability**: PostgreSQL 15.14 backend with connection pooling (1-10 connections)
- **Better Integration**: Native VS Code AI palette integration via MCP
- **Improved Performance**: JSON-RPC over stdio transport with 36/36 tests passing
- **Richer Capabilities**: 18 tools vs. limited DTM API surface

### Migration Scope

**Affected Components**:
- Agent instruction files (`.github/instructions/*.md`)
- Core documentation (`README.md`, `docs/01-15-*.md`)
- API reference documentation
- Environment configuration
- Code examples and tutorials

**Timeline**: Immediate for documentation, gradual for code deprecation

**Impact**: DTM references must be replaced with TaskMan-v2 MCP equivalents to ensure AI assistants use current architecture

---

## Architecture Changes

### Old Architecture (DTM)

```
┌─────────────────────────────────────────┐
│         Application Layer               │
├─────────────────────────────────────────┤
│         DTM API Client                  │
│         (python/dtm_api_client.py)      │
├─────────────────────────────────────────┤
│         SQLite Database                 │
│         (db/trackers.sqlite)            │
└─────────────────────────────────────────┘
```

**Characteristics**:
- Direct SQLite access
- Single-process limitations
- Limited concurrency
- No connection pooling
- Tightly coupled to CF_CLI

### New Architecture (TaskMan-v2 MCP)

```
┌─────────────────────────────────────────────────────┐
│              VS Code AI Assistants                  │
│         (GitHub Copilot, Claude, etc.)              │
├─────────────────────────────────────────────────────┤
│           MCP Protocol Layer (JSON-RPC)             │
├─────────────────────────────────────────────────────┤
│         TaskMan-v2 MCP Server                       │
│         • Python (primary): taskman-typescript      │
│         • TypeScript (alternative): task-manager    │
│         Location: TaskMan-v2/mcp-server/            │
├─────────────────────────────────────────────────────┤
│         Connection Pool (1-10 connections)          │
├─────────────────────────────────────────────────────┤
│         PostgreSQL 15.14 Database                   │
│         172.25.14.122:5432/taskman_v2               │
└─────────────────────────────────────────────────────┘
```

**Improvements**:
- MCP standardization (JSON-RPC over stdio)
- Multi-process safe with connection pooling
- PostgreSQL reliability and scalability
- VS Code native integration
- Independent server lifecycle (npm start/stop)

---

## Command Mapping

### Task Management Tools (4 core operations)

| DTM API | TaskMan-v2 MCP Tool | Description |
|---------|---------------------|-------------|
| `dtm.create_task(title, description, ...)` | `taskman-typescript.task_create` | Create new task with full metadata |
| `dtm.list_tasks(filters)` | `taskman-typescript.task_list` | Query tasks with filtering/pagination |
| `dtm.update_task(task_id, updates)` | `taskman-typescript.task_update` | Update existing task fields |
| `dtm.delete_task(task_id)` | `taskman-typescript.task_delete` | Remove task (soft delete) |

**Example - Task Creation**:

```python
# Old DTM API
task = dtm.create_task(
    title="Implement JWT authentication",
    description="Add Auth0 integration",
    priority=3,
    status="todo"
)

# New TaskMan-v2 MCP (via AI assistant)
# Use MCP tool: taskman-typescript.task_create
# Parameters:
#   title: "Implement JWT authentication"
#   description: "Add Auth0 integration"
#   priority: 3
#   status: "todo"
```

### Action List Tools (11 operations)

| DTM API | TaskMan-v2 MCP Tool | Description |
|---------|---------------------|-------------|
| `dtm.create_action_list(name)` | `taskman-typescript.action_list_create` | Create action list container |
| `dtm.list_action_lists()` | `taskman-typescript.action_list_list` | Get all action lists |
| `dtm.get_action_list(list_id)` | `taskman-typescript.action_list_get` | Retrieve specific list |
| `dtm.update_action_list(list_id, updates)` | `taskman-typescript.action_list_update` | Modify list metadata |
| `dtm.delete_action_list(list_id)` | `taskman-typescript.action_list_delete` | Remove action list |
| `dtm.add_action_item(list_id, item)` | `taskman-typescript.action_list_add_item` | Add item to list |
| `dtm.update_action_item(list_id, item_id, updates)` | `taskman-typescript.action_list_update_item` | Modify action item |
| `dtm.delete_action_item(list_id, item_id)` | `taskman-typescript.action_list_delete_item` | Remove action item |
| `dtm.reorder_items(list_id, order)` | `taskman-typescript.action_list_reorder_items` | Change item order |
| `dtm.mark_complete(list_id, item_id)` | `taskman-typescript.action_list_mark_item_complete` | Complete action item |
| `dtm.mark_incomplete(list_id, item_id)` | `taskman-typescript.action_list_mark_item_incomplete` | Reopen action item |

### Utility Tools (3 operations)

| DTM API | TaskMan-v2 MCP Tool | Description |
|---------|---------------------|-------------|
| `dtm.health_check()` | `taskman-typescript.health_check` | Verify server availability |
| `dtm.get_stats()` | `taskman-typescript.get_statistics` | Retrieve usage statistics |
| `dtm.sync()` | `taskman-typescript.sync_state` | Force synchronization |

### Resource URI Templates (4 templates)

**Direct Resource Access**:

```
# Task resources
tasks://{task_id}                    # Access specific task by ID
projects://{project_id}              # Access project with tasks
sprints://{sprint_id}                # Access sprint with tasks
action-lists://{action_list_id}      # Access action list with items
```

**Usage in MCP context**:
```yaml
# Request task resource
resource_uri: tasks://TASK-2025-001
# Returns: Full task object with metadata, description, status, etc.
```

---

## Environment Setup

### Database Configuration

**New Environment Variables** (required):

```bash
# PostgreSQL connection string
export TASKMAN_DB_URL="postgresql://user:password@172.25.14.122:5432/taskman_v2"

# Optional: Connection pool configuration
export DB_MIN_CONN=1        # Minimum connections (default: 1)
export DB_MAX_CONN=10       # Maximum connections (default: 10)
```

**PowerShell**:
```powershell
$env:TASKMAN_DB_URL = "postgresql://user:password@172.25.14.122:5432/taskman_v2"
$env:DB_MIN_CONN = "1"
$env:DB_MAX_CONN = "10"
```

### Legacy Variables to Remove

**Deprecated DTM Variables**:
```bash
# Remove these from your environment
unset DTM_API_URL
unset DTM_API_KEY
unset DTM_DB_PATH
unset DTM_SYNC_INTERVAL
```

### MCP Server Startup

**Prerequisites**:
```bash
# Navigate to MCP server directory
cd TaskMan-v2/mcp-server/

# Install dependencies (first time only)
npm install

# Start MCP server (required before task operations)
npm start
```

**Validation**:
```bash
# Check server health (should return {"status": "ok"})
curl http://localhost:3001/api/health

# Verify services running
# Expected: task-manager-api and task-manager-frontend both "online"
# Services available at:
#   • Frontend: http://localhost:5173
#   • API: http://localhost:3001
```

### VS Code Settings Configuration

**Location**: `.vscode/settings.json`

```json
{
  "mcp.servers": {
    "taskman-typescript": {
      "command": "node",
      "args": [
        "TaskMan-v2/mcp-server/dist/index.js"
      ],
      "env": {
        "TASKMAN_DB_URL": "postgresql://user:password@172.25.14.122:5432/taskman_v2",
        "DB_MIN_CONN": "1",
        "DB_MAX_CONN": "10"
      }
    }
  }
}
```

---

## VS Code Integration

### MCP Server Registration

**Step 1: Configure Server in settings.json** (see above)

**Step 2: Restart VS Code**
- Command: `Developer: Reload Window` (Ctrl+R)
- Ensures MCP server registration takes effect

**Step 3: Verify Registration**
- Open GitHub Copilot chat
- Type `/` to see available tools
- Look for `taskman-typescript` tools in completion list

### Using TaskMan-v2 MCP Tools

**In AI Assistant Chat**:

```
User: "Create a new task for implementing JWT authentication with priority 3"

AI Assistant: I'll use the taskman-typescript.task_create tool...

[Tool invocation happens automatically via MCP protocol]

Result: Created task TASK-2025-001 "Implement JWT authentication"
```

**Explicit Tool Request**:

```
User: "Use taskman-typescript.task_list to show all tasks with status 'in_progress'"

AI Assistant: [Executes MCP tool call with filter parameters]

Result:
- TASK-2025-001: Implement JWT authentication (priority: 3)
- TASK-2025-005: Database migration (priority: 4)
- TASK-2025-012: API documentation (priority: 2)
```

### Fallback to CF_CLI

**When MCP Unavailable** (server not started, connection issues):

```bash
# CF_CLI provides secondary access path
python cf_cli.py task create --title "Implement JWT authentication" --priority 3
python cf_cli.py task list --status in_progress
python cf_cli.py task update TASK-2025-001 --status completed
```

**Decision Tree**:
1. **Check MCP availability** → Use `taskman-typescript` tools (preferred)
2. **If MCP unavailable** → Fall back to `cf_cli.py` commands
3. **Log decision** → Document which path taken for audit trail

---

## Troubleshooting

### Common Issues and Resolutions

#### Issue 1: MCP Server Not Found

**Symptoms**:
- AI assistant reports "Tool not found: taskman-typescript.task_create"
- MCP tools don't appear in completion list

**Diagnosis**:
```bash
# Check if server is running
ps aux | grep "node.*TaskMan-v2"

# Check VS Code settings
cat .vscode/settings.json | grep "taskman-typescript"
```

**Resolution**:
```bash
# Start MCP server
cd TaskMan-v2/mcp-server/
npm start

# Restart VS Code
# Command: Developer: Reload Window (Ctrl+R)
```

#### Issue 2: Database Connection Failed

**Symptoms**:
- MCP server starts but tools return "Connection refused"
- Health check fails: `curl http://localhost:3001/api/health` returns error

**Diagnosis**:
```bash
# Verify environment variable set
echo $TASKMAN_DB_URL

# Test database connectivity
psql $TASKMAN_DB_URL -c "SELECT 1;"
```

**Resolution**:
```bash
# Correct connection string format
export TASKMAN_DB_URL="postgresql://user:password@172.25.14.122:5432/taskman_v2"

# Restart MCP server
cd TaskMan-v2/mcp-server/
npm restart
```

#### Issue 3: Authentication Errors

**Symptoms**:
- Tools return "Authentication failed" or "Permission denied"
- Database queries fail with access errors

**Diagnosis**:
```bash
# Check database user permissions
psql $TASKMAN_DB_URL -c "\du"

# Verify user has access to taskman_v2 database
psql $TASKMAN_DB_URL -c "\l"
```

**Resolution**:
```sql
-- Grant necessary permissions (run as postgres superuser)
GRANT CONNECT ON DATABASE taskman_v2 TO taskman_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO taskman_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO taskman_user;
```

#### Issue 4: Port Conflicts

**Symptoms**:
- MCP server fails to start with "EADDRINUSE" error
- Port 3001 or 5173 already in use

**Diagnosis**:
```bash
# Check which process is using the port
netstat -ano | findstr :3001   # Windows
lsof -i :3001                   # Linux/Mac
```

**Resolution**:
```bash
# Kill conflicting process (Windows)
taskkill /PID <process_id> /F

# Kill conflicting process (Linux/Mac)
kill -9 <process_id>

# Or configure different port in server config
```

#### Issue 5: Stale Connection Pool

**Symptoms**:
- Queries hang or timeout
- "Connection pool exhausted" errors

**Diagnosis**:
```bash
# Check active connections
psql $TASKMAN_DB_URL -c "SELECT count(*) FROM pg_stat_activity WHERE datname='taskman_v2';"
```

**Resolution**:
```bash
# Restart MCP server (clears pool)
cd TaskMan-v2/mcp-server/
npm restart

# Or increase pool size
export DB_MAX_CONN=20
npm restart
```

---

## Rollback Procedures

### When to Rollback

**Criteria for rollback**:
- Critical functionality broken after migration
- Database connection issues unresolved within 30 minutes
- AI assistants unable to access task management
- User productivity severely impacted

### Rollback Steps

#### Step 1: Revert Environment Variables

```bash
# Remove TaskMan-v2 MCP variables
unset TASKMAN_DB_URL
unset DB_MIN_CONN
unset DB_MAX_CONN

# Restore DTM variables (if needed for legacy code)
export DTM_API_URL="http://localhost:8080"
export DTM_DB_PATH="db/trackers.sqlite"
```

#### Step 2: Revert VS Code Settings

```json
// Remove from .vscode/settings.json
{
  "mcp.servers": {
    // Delete "taskman-typescript" configuration
  }
}
```

**Restart VS Code**: `Developer: Reload Window` (Ctrl+R)

#### Step 3: Revert Documentation Changes

```bash
# Restore previous versions from git
git checkout HEAD~1 .github/instructions/Sequential-Thinking.instructions.md
git checkout HEAD~1 .github/copilot-instructions.md
git checkout HEAD~1 AGENTS.md
git checkout HEAD~1 README.md
```

#### Step 4: Stop TaskMan-v2 MCP Server

```bash
cd TaskMan-v2/mcp-server/
npm stop

# Or force kill
pkill -f "node.*TaskMan-v2"
```

#### Step 5: Validate Rollback

**Verification Checklist**:
- [ ] Environment variables reverted (check with `env | grep TASKMAN`)
- [ ] VS Code settings clean (no taskman-typescript references)
- [ ] Documentation reverted to DTM references
- [ ] MCP server stopped (no processes running)
- [ ] Legacy DTM code accessible (if needed)
- [ ] AI assistants functioning (even if with degraded features)

**Re-Migration**: If rollback successful, investigate root cause before re-attempting migration. Document issues in `docs/migration/rollback-report-YYYYMMDD.md` for future reference.

---

## Migration Checklist

### Pre-Migration

- [ ] Review this migration guide completely
- [ ] Backup current environment variables (`env > backup_env.txt`)
- [ ] Backup VS Code settings (`.vscode/settings.json`)
- [ ] Verify PostgreSQL database accessible (`psql $TASKMAN_DB_URL -c "SELECT 1;"`)
- [ ] Install TaskMan-v2 MCP server dependencies (`cd TaskMan-v2/mcp-server/ && npm install`)

### Migration

- [ ] Update environment variables (TASKMAN_DB_URL, DB_MIN_CONN, DB_MAX_CONN)
- [ ] Remove legacy DTM variables (DTM_API_*, DTM_DB_PATH)
- [ ] Configure VS Code settings.json with MCP server registration
- [ ] Start TaskMan-v2 MCP server (`npm start`)
- [ ] Validate health check (`curl http://localhost:3001/api/health`)
- [ ] Restart VS Code (`Developer: Reload Window`)
- [ ] Test MCP tools in AI assistant (task_create, task_list)

### Post-Migration Validation

- [ ] All AI assistants can access taskman-typescript tools
- [ ] Task creation/update/delete operations working
- [ ] Action list operations functional
- [ ] Resource URIs resolving correctly (tasks://{id}, projects://{id})
- [ ] CF_CLI fallback working if MCP unavailable
- [ ] No errors in MCP server logs
- [ ] Documentation references consistent (no DTM mentions)

### Monitoring (First 48 Hours)

- [ ] Monitor MCP server logs for errors
- [ ] Track database connection pool utilization
- [ ] Verify AI assistant task management usage patterns
- [ ] Document any unexpected issues
- [ ] Collect user feedback on migration impact

---

## Additional Resources

### Documentation

- **TaskMan-v2 MCP Architecture**: `TaskMan-v2/mcp-server/README.md`
- **MCP Protocol Specification**: [Model Context Protocol Documentation](https://github.com/modelcontextprotocol/specification)
- **Agent Instructions Best Practices**: `docs/MCP-Agent-Instructions-Best-Practices.md`
- **ContextForge Work Codex**: `docs/Codex/ContextForge Work Codex.md`

### Support

- **GitHub Issues**: Report migration issues at repository issue tracker
- **Database Issues**: Contact database administrator for PostgreSQL connectivity
- **MCP Server Issues**: Check `TaskMan-v2/mcp-server/logs/` for diagnostic information

### Migration History

- **2025-11-16**: Initial migration guide created
- **2025-11-16**: Sequential-Thinking.instructions.md updated (DTM → TaskMan-v2 MCP)
- **[Future]**: Core documentation updates (Phase 1-2 tasks)

---

**Document Status**: Production Guidance ✅
**Authoritative**: Yes (primary migration reference for all DTM → TaskMan-v2 MCP transitions)
**Next Review**: 2025-12-16 (30-day post-migration validation)
**Maintained By**: ContextForge Architecture Team
