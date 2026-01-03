---
applyTo: "database*, db*, postgres*, psql*, sql*, query*"
description: "Direct database access patterns for PostgreSQL TaskMan-v2 database"
---

# Database Access Instructions

**Authority**: Database access checklist complete | **Version**: 1.0 | **Date**: 2025-12-29

---

## Core Principle

**Use direct database access** instead of MCP database servers for better performance, simplicity, and reliability.

### Performance Baseline
- ✅ **Python Direct**: 168ms P95 (recommended for automation)
- ✅ **Docker Exec**: 223ms P95 (+33% overhead, good for ad-hoc queries)
- ❌ **MCP Server**: Deprecated (adds +15-45% overhead + complexity)

---

## Connection Details

### TaskMan-v2 Database (Primary)

```yaml
Host: localhost
Port: 5434
User: contextforge
Password: contextforge
Database: taskman_v2
Connection String: postgresql://contextforge:contextforge@localhost:5434/taskman_v2
```

### Other Databases

```yaml
ContextForge:
  Port: 5433
  Database: contextforge

Sacred Context:
  Port: 5432
  Database: sacred_context
```

---

## Method 1: Docker Exec (Recommended for AI Agents)

### Why Use This
- ✅ No setup required
- ✅ Works across all AI platforms (Claude Desktop, GitHub Copilot, Gemini)
- ✅ Single command execution
- ✅ Self-contained (credentials in container)

### Basic Pattern

```bash
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "YOUR_SQL_QUERY"
```

### Examples

```bash
# Count all tasks
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"
# Output: 9

# Get active tasks
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT id, title, status FROM tasks WHERE status = 'new' LIMIT 5;"

# Aggregate by status
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT status, COUNT(*) FROM tasks GROUP BY status;"
# Output: new: 8, done: 1

# Join with sprints
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT t.id, t.title, s.name FROM tasks t LEFT JOIN sprints s ON t.sprint_id = s.id LIMIT 10;"

# Schema inspection
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "\dt"
```

### Interactive Shell

```bash
# Open psql interactive shell
docker exec -it taskman-postgres psql -U contextforge -d taskman_v2

# Inside shell:
# \dt              -- List tables
# \d tasks         -- Describe tasks table
# \l               -- List databases
# SELECT * FROM tasks LIMIT 5;
# \q               -- Exit
```

### Error Handling

```bash
# Check if container is running first
if docker ps | grep -q taskman-postgres; then
  docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"
else
  echo "Error: Container not running. Start with: docker start taskman-postgres"
  exit 1
fi
```

---

## Method 2: Python Direct Connection (Recommended for Scripts)

### Why Use This
- ✅ Best performance (168ms P95)
- ✅ Full psycopg2 capabilities
- ✅ Proper connection pooling
- ✅ Transaction support

### Getting Credentials

```python
import subprocess

# Get connection string from helper
result = subprocess.run(
    ['python', 'scripts/db_auth.py'],
    capture_output=True,
    text=True,
    check=True
)
connection_string = result.stdout.strip()
# Returns: postgresql://contextforge:contextforge@localhost:5434/taskman_v2
```

### Basic Pattern

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Connect
conn = psycopg2.connect("postgresql://contextforge:contextforge@localhost:5434/taskman_v2")
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Execute query
cursor.execute("SELECT id, title, status FROM tasks WHERE status = %s", ('new',))
rows = cursor.fetchall()

# Process results
for row in rows:
    print(f"{row['id']}: {row['title']} ({row['status']})")

# Cleanup
cursor.close()
conn.close()
```

### With Context Manager (Recommended)

```python
import psycopg2
from contextlib import closing

with closing(psycopg2.connect("postgresql://contextforge:contextforge@localhost:5434/taskman_v2")) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        print(f"Total tasks: {count}")
```

### INSERT/UPDATE/DELETE Pattern

```python
import psycopg2

conn = psycopg2.connect("postgresql://contextforge:contextforge@localhost:5434/taskman_v2")
cursor = conn.cursor()

try:
    # Insert new task
    cursor.execute("""
        INSERT INTO tasks (id, title, status, priority, created_at, updated_at)
        VALUES (gen_random_uuid(), %s, %s, %s, NOW(), NOW())
        RETURNING id, title
    """, ('New Task', 'new', 3))

    new_task = cursor.fetchone()
    print(f"Created task: {new_task}")

    # Commit transaction
    conn.commit()

except Exception as e:
    # Rollback on error
    conn.rollback()
    print(f"Error: {e}")

finally:
    cursor.close()
    conn.close()
```

### Async Pattern (Optional)

```python
import asyncio
import asyncpg

async def query_tasks():
    conn = await asyncpg.connect("postgresql://contextforge:contextforge@localhost:5434/taskman_v2")
    try:
        rows = await conn.fetch("SELECT id, title FROM tasks LIMIT 10")
        for row in rows:
            print(dict(row))
    finally:
        await conn.close()

asyncio.run(query_tasks())
```

---

## Method 3: PowerShell (Windows Automation)

### Getting Credentials

```powershell
# Load credential helper
. scripts/Get-DatabaseCredentials.ps1

# Get connection string
$connStr = Get-PostgreSQLConnectionString -Database 'taskman_v2'
# Returns: Server=localhost;Port=5434;Database=taskman_v2;User Id=contextforge;Password=contextforge
```

### Using Docker Exec from PowerShell

```powershell
# Simple query
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"

# With error handling
try {
    $result = docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Query successful: $result"
    } else {
        Write-Error "Query failed: $result"
    }
} catch {
    Write-Error "Container error: $_"
}
```

### Using Npgsql (Advanced)

```powershell
# Requires: Install-Module -Name Npgsql

Add-Type -Path "C:\path\to\Npgsql.dll"

$connStr = "Host=localhost;Port=5434;Database=taskman_v2;Username=contextforge;Password=contextforge"
$conn = New-Object Npgsql.NpgsqlConnection($connStr)

try {
    $conn.Open()

    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "SELECT COUNT(*) FROM tasks"
    $count = $cmd.ExecuteScalar()

    Write-Host "Total tasks: $count"

} catch {
    Write-Error "Database error: $_"
} finally {
    $conn.Close()
}
```

---

## Common Query Patterns

### Read Operations

```sql
-- Count records
SELECT COUNT(*) FROM tasks;

-- Filter by status
SELECT id, title, status FROM tasks WHERE status = 'new';

-- Pagination
SELECT id, title, created_at FROM tasks ORDER BY created_at DESC LIMIT 10 OFFSET 0;

-- Search (case-insensitive)
SELECT id, title FROM tasks WHERE title ILIKE '%authentication%';

-- Join
SELECT t.id, t.title, s.name AS sprint_name
FROM tasks t
LEFT JOIN sprints s ON t.sprint_id = s.id;

-- Aggregate
SELECT status, COUNT(*) as count, AVG(priority) as avg_priority
FROM tasks
GROUP BY status
ORDER BY count DESC;
```

### Write Operations

```sql
-- Insert
INSERT INTO tasks (id, title, status, priority, created_at, updated_at)
VALUES (gen_random_uuid(), 'New Task', 'new', 3, NOW(), NOW())
RETURNING id, title;

-- Update
UPDATE tasks
SET status = 'in_progress', updated_at = NOW()
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
RETURNING id, title, status;

-- Delete (use with caution!)
DELETE FROM tasks
WHERE status = 'done' AND updated_at < NOW() - INTERVAL '90 days'
RETURNING id, title;

-- Upsert (insert or update)
INSERT INTO tasks (id, title, status, priority, created_at, updated_at)
VALUES ('123e4567-e89b-12d3-a456-426614174000', 'Task Title', 'new', 3, NOW(), NOW())
ON CONFLICT (id)
DO UPDATE SET
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    updated_at = NOW()
RETURNING *;
```

### Schema Inspection

```sql
-- List tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Describe table
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'tasks'
ORDER BY ordinal_position;

-- Table row counts
SELECT schemaname, tablename, n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;

-- Database size
SELECT pg_size_pretty(pg_database_size('taskman_v2')) AS size;
```

---

## Database Schema (9 Tables)

```
taskman_v2
├── tasks            (9 rows)  - Core task management
│   ├── id (uuid, PK)
│   ├── title (varchar 255, NOT NULL)
│   ├── description (text)
│   ├── status (varchar 50, default 'new')
│   ├── priority (integer, default 3)
│   ├── created_at (timestamp, default NOW())
│   ├── updated_at (timestamp, default NOW())
│   ├── sprint_id (uuid, FK -> sprints.id)
│   └── project_id (uuid, FK -> projects.id)
├── sprints          (0 rows)  - Sprint planning
├── projects         (0 rows)  - Project hierarchy
├── tags             (0 rows)  - Task tagging
├── task_tags        (0 rows)  - Many-to-many task↔tag
├── comments         (0 rows)  - Task comments
├── attachments      (0 rows)  - File attachments
├── time_entries     (0 rows)  - Time tracking
└── audit_log        (0 rows)  - Change history
```

---

## Troubleshooting

### Container Not Running

```bash
# Check status
docker ps | grep taskman-postgres

# Start if stopped
docker start taskman-postgres

# Verify healthy
docker ps --filter name=taskman-postgres --format "{{.Status}}"

# Quick restart script
pwsh -File scripts/Restart-Docker.ps1
```

### Connection Refused

```bash
# Check port is listening
netstat -an | findstr 5434  # Windows
netstat -an | grep 5434     # Linux/Mac

# Verify port mapping
docker port taskman-postgres
# Expected: 5432/tcp -> 0.0.0.0:5434

# Test connection
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT 1;"
```

### Authentication Failed

```bash
# Verify credentials (hardcoded in development)
# Username: contextforge
# Password: contextforge

# Test login
docker exec -it taskman-postgres psql -U contextforge -d taskman_v2

# Check environment variables
docker inspect taskman-postgres | grep -A 5 "Env"
```

### Database Does Not Exist

```bash
# List databases
docker exec taskman-postgres psql -U contextforge -d postgres -c "\l"

# Create if missing
docker exec taskman-postgres psql -U contextforge -d postgres -c "CREATE DATABASE taskman_v2 OWNER contextforge;"

# Verify tables exist
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "\dt"
```

**Complete troubleshooting guide**: See [docs/DATABASE-TROUBLESHOOTING-FLOWCHART.md](../docs/DATABASE-TROUBLESHOOTING-FLOWCHART.md)

---

## Security Considerations

### Development Environment
- ✅ Hardcoded credentials (contextforge/contextforge) acceptable
- ✅ Containers bound to localhost only
- ✅ No external network exposure

### Production Environment
- ⚠️ **NEVER** use hardcoded credentials
- ✅ Use environment variables or secret managers
- ✅ Enable SSL/TLS connections
- ✅ Implement connection pooling
- ✅ Use read-only users for queries
- ✅ Configure automated backups

**Full security review**: See [docs/DATABASE-SECURITY-REVIEW.md](../docs/DATABASE-SECURITY-REVIEW.md)

---

## Performance Tips

### For AI Agents
1. Use `LIMIT` clauses to prevent overwhelming output
2. Prefer `COUNT(*)` over `SELECT *` when checking for existence
3. Use prepared statements for repeated queries
4. Close connections promptly

### For Developers
1. Use Python direct connection for best performance (168ms P95)
2. Enable connection pooling for high-throughput applications
3. Add indexes on frequently filtered columns
4. Use `EXPLAIN ANALYZE` to optimize slow queries
5. Run `ANALYZE` after bulk inserts

### Query Optimization

```sql
-- Check query performance
EXPLAIN ANALYZE SELECT * FROM tasks WHERE status = 'new';

-- Create index if needed
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

-- Update statistics
ANALYZE tasks;
```

**Full performance analysis**: See [docs/DATABASE-PERFORMANCE-REPORT.md](../docs/DATABASE-PERFORMANCE-REPORT.md)

---

## AI Agent Best Practices

### Before Every Query
1. ✅ Verify container is running: `docker ps | grep taskman-postgres`
2. ✅ Use `try/catch` for error handling
3. ✅ Limit results with `LIMIT` clause
4. ✅ Use parameterized queries to prevent SQL injection

### Query Execution Checklist
```mermaid
flowchart LR
    A[Query Request] --> B{Container<br/>running?}
    B -->|No| C[Start container]
    B -->|Yes| D[Execute query]
    C --> D
    D --> E{Success?}
    E -->|Yes| F[Return results]
    E -->|No| G[Log error &<br/>return diagnostic]
```

### Example: Safe Query Execution

```python
import subprocess
import psycopg2

def safe_query(sql, params=None):
    """Execute SQL query with error handling."""
    try:
        # Check container
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'taskman-postgres' not in result.stdout:
            return {"error": "Container not running. Run: docker start taskman-postgres"}

        # Execute query
        conn = psycopg2.connect("postgresql://contextforge:contextforge@localhost:5434/taskman_v2")
        cursor = conn.cursor()
        cursor.execute(sql, params)

        # Fetch results
        if sql.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            return {"success": True, "rows": rows, "count": len(rows)}
        else:
            conn.commit()
            return {"success": True, "message": "Query executed"}

    except Exception as e:
        return {"error": str(e), "sql": sql}
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Usage
result = safe_query("SELECT COUNT(*) FROM tasks WHERE status = %s", ('new',))
print(result)
```

---

## Related Documentation

### Quick Access
- **Quick Reference (1 page)**: [docs/DATABASE-QUICK-REFERENCE.md](../docs/DATABASE-QUICK-REFERENCE.md)
- **Example Queries Library**: [docs/DATABASE-EXAMPLE-QUERIES.md](../docs/DATABASE-EXAMPLE-QUERIES.md)
- **Troubleshooting Flowchart**: [docs/DATABASE-TROUBLESHOOTING-FLOWCHART.md](../docs/DATABASE-TROUBLESHOOTING-FLOWCHART.md)

### Comprehensive Guides
- **Agent Database Access Guide** (500+ lines): [docs/AGENT-DATABASE-ACCESS.md](../docs/AGENT-DATABASE-ACCESS.md)
- **Performance Analysis**: [docs/DATABASE-PERFORMANCE-REPORT.md](../docs/DATABASE-PERFORMANCE-REPORT.md)
- **Security Review**: [docs/DATABASE-SECURITY-REVIEW.md](../docs/DATABASE-SECURITY-REVIEW.md)
- **Production Deployment**: [docs/PRODUCTION-DEPLOYMENT-SECURITY.md](../docs/PRODUCTION-DEPLOYMENT-SECURITY.md)

### Project Resources
- **Agent Examples**: [AGENTS.md](../AGENTS.md#database-access)
- **Database Access Checklist**: [DATABASE-ACCESS-CHECKLIST.md](../DATABASE-ACCESS-CHECKLIST.md)

---

## Key Takeaways

1. **Use docker exec for ad-hoc queries** (223ms P95, works everywhere)
2. **Use Python direct for automation** (168ms P95, best performance)
3. **Credentials are contextforge/contextforge** (development only)
4. **9 tables in taskman_v2 database** (9 tasks currently)
5. **Container must be running** (check with `docker ps`)
6. **See troubleshooting flowchart** for common issues

---

**Last Updated**: 2025-12-29 | **Authority**: DATABASE-ACCESS-CHECKLIST.md Phase 1-7 Complete
