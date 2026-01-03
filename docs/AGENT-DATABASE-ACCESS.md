# Agent Database Access Guide

**Quick Reference for AI Coding Agents**

This guide shows how AI agents (Claude Desktop, GitHub Copilot, Gemini) should access ContextForge databases efficiently using direct methods instead of MCP servers.

---

## 🎯 Why Direct Access?

**Simple**: AI → Database (one hop, ~0.1s latency)
**Fast**: No middleware overhead
**Reliable**: No MCP server configuration to maintain
**Platform Agnostic**: Works with Claude, Copilot, Gemini equally

---

## 📊 Available Databases

| Database | Type | Port | Container | Purpose |
|----------|------|------|-----------|---------|
| **taskman_v2** | PostgreSQL 16 | 5434 | taskman-postgres | TaskMan-v2 (PRIMARY) |
| **contextforge** | PostGIS 15 | 5433 | contextforge-postgres | ContextForge project |
| **context_forge** | PostgreSQL 15 | 5432 | sacred-context-db | Sacred Geometry |
| **taskman.db** | SQLite | - | File | Legacy task data |
| **velocity.duckdb** | DuckDB | - | File | Velocity tracking |
| **dashboard_history.duckdb** | DuckDB | - | File | Dashboard metrics |

**Credentials (all containers)**: `contextforge` / `contextforge`

---

## 🚀 Quick Start - 3 Methods

### Method 1: Docker Exec (Fastest - Recommended)

**Best for**: One-off queries, exploration, debugging

```bash
# Basic query
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"

# Pretty formatted output
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT id, title, status FROM tasks LIMIT 5;"

# Multiple commands
docker exec -it taskman-postgres psql -U contextforge -d taskman_v2
# Now you're in interactive psql shell
```

### Method 2: Python with Credential Helper

**Best for**: Python scripts, data analysis, automation

```python
from scripts.db_auth import get_db_credentials
import psycopg2

# Get connection string
url = get_db_credentials('postgresql', format='url')
# postgresql://contextforge:contextforge@localhost:5434/taskman_v2

# Connect and query
conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM tasks;")
print(cur.fetchone())  # (9,)
conn.close()
```

### Method 3: PowerShell with Credential Helper

**Best for**: PowerShell scripts, Windows automation, admin tasks

```powershell
# Get credentials
$creds = . scripts/Get-DatabaseCredentials.ps1

# Use connection string
Write-Host $creds.PostgreSQL.ConnectionString
# postgresql://contextforge:contextforge@localhost:5434/taskman_v2

# Or use individual components
$env:PG_HOST = $creds.PostgreSQL.Host
$env:PG_PORT = $creds.PostgreSQL.Port
$env:PG_USER = $creds.PostgreSQL.User
# etc.
```

---

## 📚 Common Query Patterns

### SELECT - Read Data

```sql
-- Count records
SELECT COUNT(*) FROM tasks;

-- Get all tasks with status
SELECT id, title, status, priority FROM tasks WHERE status = 'in_progress';

-- Join with sprints
SELECT t.title, s.name AS sprint_name
FROM tasks t
LEFT JOIN sprints s ON t.sprint_id = s.id;
```

### INSERT - Create Data

```sql
-- Insert new task
INSERT INTO tasks (id, title, status, priority, created_at)
VALUES ('TASK-TEST-001', 'Test Task', 'todo', 3, NOW())
RETURNING id, title;
```

### UPDATE - Modify Data

```sql
-- Update task status
UPDATE tasks
SET status = 'completed', updated_at = NOW()
WHERE id = 'TASK-001'
RETURNING id, status;
```

### DELETE - Remove Data

```sql
-- Delete test task
DELETE FROM tasks
WHERE id = 'TASK-TEST-001'
RETURNING id;
```

---

## 🔍 Database Schema Reference

### TaskMan-v2 Tables (9 tables)

```sql
-- List all tables
\dt

-- Table details
\d tasks
\d sprints
\d projects
\d action_lists
\d checklists
\d conversation_sessions
\d conversation_turns
\d plans
\d alembic_version
```

### Common Columns

**tasks**:
- `id` (VARCHAR) - Primary key (e.g., 'TASK-001')
- `title` (VARCHAR) - Task title
- `description` (TEXT) - Full description
- `status` (VARCHAR) - todo, in_progress, completed, blocked
- `priority` (INTEGER) - 1-5
- `sprint_id` (VARCHAR) - Foreign key to sprints
- `created_at`, `updated_at` (TIMESTAMP)

**sprints**:
- `id` (VARCHAR) - Primary key (e.g., 'S-001')
- `name` (VARCHAR) - Sprint name
- `start_date`, `end_date` (DATE)
- `status` (VARCHAR) - planning, active, completed

---

## 🎨 Examples by AI Platform

### Claude Desktop

```markdown
User: "How many tasks are in the database?"

Claude: I'll query the database directly.
```
```bash
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"
```
```markdown
Result: 9 tasks found.
```

### GitHub Copilot (VS Code)

```python
# Copilot suggestion when you type:
# "Get all tasks with their sprint names"

from scripts.db_auth import get_db_credentials
import psycopg2

url = get_db_credentials('postgresql', format='url')
conn = psycopg2.connect(url)
cur = conn.cursor()

query = """
    SELECT t.id, t.title, s.name AS sprint_name
    FROM tasks t
    LEFT JOIN sprints s ON t.sprint_id = s.id
    ORDER BY t.created_at DESC;
"""

cur.execute(query)
tasks = cur.fetchall()
for task in tasks:
    print(f"{task[0]}: {task[1]} (Sprint: {task[2]})")
```

### Gemini with Antigravity

```bash
# Gemini executing shell command
docker exec taskman-postgres psql -U contextforge -d taskman_v2 << EOF
SELECT status, COUNT(*) as count
FROM tasks
GROUP BY status
ORDER BY count DESC;
EOF
```

---

## 🧪 Testing Database Access

### Quick Health Check

```bash
# 1. Verify containers running
docker ps --filter "name=postgres"

# 2. Test connection
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT version();"

# 3. Count tables
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "\dt"

# 4. Query sample data
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"
```

### Python Connection Test

```bash
python scripts/db_auth.py
# Should output PostgreSQL connection string and environment variables
```

### PowerShell Connection Test

```powershell
. scripts/Get-DatabaseCredentials.ps1
# Should output connection details for all databases
```

---

## 🛠️ Troubleshooting

### Issue: Container not running

```bash
# Check status
docker ps --filter "name=taskman-postgres"

# Start container
docker start taskman-postgres

# Or restart Docker Desktop
scripts/Restart-Docker.ps1
```

### Issue: Permission denied

```bash
# Verify credentials
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT current_user;"

# Should return: contextforge
```

### Issue: Database not found

```bash
# List databases
docker exec taskman-postgres psql -U contextforge -d postgres -c "\l"

# Should show taskman_v2 database
```

### Issue: Connection refused

```bash
# Check port mapping
docker ps --filter "name=taskman-postgres" --format "{{.Ports}}"

# Should show: 0.0.0.0:5434->5432/tcp
```

### Issue: Wrong port

Remember the correct ports:
- **TaskMan-v2**: Port **5434** (taskman-postgres)
- **ContextForge**: Port 5433 (contextforge-postgres)
- **Sacred Geometry**: Port 5432 (sacred-context-db)

---

## 🔐 Security Best Practices

### Development vs Production

**Current Setup (Development)**:
- Credentials: `contextforge/contextforge` (simple, local only)
- Containers: Exposed on localhost only
- Network: Docker bridge network (isolated)

**For Production**:
- Use environment variables for credentials
- Rotate passwords regularly
- Use connection pooling
- Enable SSL/TLS
- Restrict port exposure
- Use secrets management (Azure Key Vault, AWS Secrets Manager)

### Credential Helper Security

```python
# Good: Use credential helper
from scripts.db_auth import get_db_credentials
url = get_db_credentials('postgresql')

# Bad: Hardcode credentials
url = "postgresql://contextforge:contextforge@localhost:5434/taskman_v2"  # Don't do this in production
```

---

## 📈 Performance Tips

### Use Connection Pooling

```python
from psycopg2 import pool

# Create connection pool
db_pool = pool.SimpleConnectionPool(
    1, 20,  # min=1, max=20 connections
    get_db_credentials('postgresql', format='url')
)

# Get connection from pool
conn = db_pool.getconn()
# ... use connection ...
db_pool.putconn(conn)
```

### Optimize Queries

```sql
-- Bad: No WHERE clause
SELECT * FROM tasks;

-- Good: Filter early
SELECT id, title, status FROM tasks WHERE status = 'in_progress';

-- Bad: N+1 queries
-- Good: Use JOIN
SELECT t.*, s.name FROM tasks t LEFT JOIN sprints s ON t.sprint_id = s.id;
```

### Use Prepared Statements

```python
# Prevents SQL injection and improves performance
cur.execute(
    "SELECT * FROM tasks WHERE status = %s AND priority >= %s",
    ('in_progress', 3)
)
```

---

## 🔗 Related Documentation

- **Credential Helpers**:
  - Python: `scripts/db_auth.py`
  - PowerShell: `scripts/Get-DatabaseCredentials.ps1`
- **Docker Management**: `scripts/Restart-Docker.ps1`
- **Database Schema**: See table definitions in database
- **Migration Files**: `TaskMan-v2/backend-api/alembic/versions/`

---

## 📞 Quick Command Reference

```bash
# === DOCKER COMMANDS ===
docker ps --filter "name=postgres"                    # List PostgreSQL containers
docker start taskman-postgres                         # Start container
docker exec -it taskman-postgres psql -U contextforge -d taskman_v2  # Interactive shell

# === QUERY EXAMPLES ===
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "\dt"  # List tables
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "\d tasks"  # Describe table

# === CREDENTIAL HELPERS ===
python scripts/db_auth.py                             # Python helper
. scripts/Get-DatabaseCredentials.ps1                  # PowerShell helper

# === HEALTH CHECKS ===
scripts/Restart-Docker.ps1 -Method Diagnostic         # Full Docker diagnostic
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT version();"
```

---

**Last Updated**: 2025-12-29
**Status**: Active - Direct access method (no MCP)
**Maintained By**: ContextForge Team
