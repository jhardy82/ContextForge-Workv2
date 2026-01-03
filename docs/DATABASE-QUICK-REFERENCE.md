# Database Access Quick Reference

**Version**: 1.0 | **Date**: 2025-12-29 | **Project**: ContextForge TaskMan-v2

---

## 🚀 Quick Start (30 Seconds)

### Connection Details

| Database | Host | Port | User | Password | Database |
|----------|------|------|------|----------|----------|
| **TaskMan-v2** | localhost | 5434 | contextforge | contextforge | taskman_v2 |
| ContextForge | localhost | 5433 | contextforge | contextforge | contextforge |
| Sacred Context | localhost | 5432 | contextforge | contextforge | sacred_context |

### Fastest Query Method

```bash
# Run any SQL query instantly (copy-paste ready)
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT COUNT(*) FROM tasks;"
```

---

## 📖 Three Access Methods

### Method 1: Docker Exec (Recommended for Ad-Hoc Queries)

**Performance**: 223ms P95 | **Use When**: Quick debugging, manual inspection

```bash
# Basic SELECT
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT * FROM tasks LIMIT 5;"

# With formatting
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT id, title, status FROM tasks;" -x

# Multiple commands
docker exec -it taskman-postgres psql -U contextforge -d taskman_v2
# Now in psql shell:
# \dt          -- List tables
# \d tasks     -- Describe tasks table
# SELECT * FROM tasks;
# \q           -- Exit
```

### Method 2: Python Script (Recommended for Automation)

**Performance**: 168ms P95 | **Use When**: Scripts, automation, data processing

```python
# Get credentials
import subprocess
conn_str = subprocess.check_output(['python', 'scripts/db_auth.py'], text=True).strip()
# Result: postgresql://contextforge:contextforge@localhost:5434/taskman_v2

# Use with psycopg2
import psycopg2
conn = psycopg2.connect(conn_str)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM tasks")
print(cursor.fetchone()[0])  # Output: 9
cursor.close()
conn.close()
```

### Method 3: PowerShell Script (Recommended for Windows Automation)

**Use When**: PowerShell scripts, Windows automation

```powershell
# Get credentials
. scripts/Get-DatabaseCredentials.ps1
$connStr = Get-PostgreSQLConnectionString -Database 'taskman_v2'
# Result: Server=localhost;Port=5434;Database=taskman_v2;User Id=contextforge;Password=contextforge

# Use with Npgsql (requires module)
# Install-Module -Name Npgsql
$conn = New-Object Npgsql.NpgsqlConnection($connStr)
$conn.Open()
$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT COUNT(*) FROM tasks"
$result = $cmd.ExecuteScalar()
Write-Host "Task count: $result"
$conn.Close()
```

---

## 🎯 Common Query Patterns

### Read Operations (SELECT)

```sql
-- Count all tasks
SELECT COUNT(*) FROM tasks;
-- Result: 9

-- Filter by status
SELECT id, title, status FROM tasks WHERE status = 'new';
-- Result: 8 rows

-- Join with sprints
SELECT t.id, t.title, s.name AS sprint_name
FROM tasks t
LEFT JOIN sprints s ON t.sprint_id = s.id
LIMIT 10;

-- Aggregate by status
SELECT status, COUNT(*) as count
FROM tasks
GROUP BY status
ORDER BY count DESC;
-- Result: new: 8, done: 1
```

### Write Operations (INSERT/UPDATE/DELETE)

```sql
-- Insert new task
INSERT INTO tasks (id, title, status, priority, created_at, updated_at)
VALUES (gen_random_uuid(), 'New Task', 'new', 3, NOW(), NOW())
RETURNING id, title;

-- Update task status
UPDATE tasks
SET status = 'in_progress', updated_at = NOW()
WHERE id = '123e4567-e89b-12d3-a456-426614174000';

-- Delete completed tasks (use carefully!)
DELETE FROM tasks WHERE status = 'done' AND updated_at < NOW() - INTERVAL '30 days';
```

### Schema Inspection

```sql
-- List all tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Describe table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks'
ORDER BY ordinal_position;

-- Check table row counts
SELECT
    schemaname,
    tablename,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

---

## 🛠️ Troubleshooting (30-Second Fixes)

### ❌ Error: "connection refused"

```bash
# 1. Check if container is running
docker ps | grep taskman-postgres

# 2. If not running, restart it
docker start taskman-postgres

# 3. Verify port 5434 is listening
netstat -an | findstr 5434  # Windows
netstat -an | grep 5434     # Linux/Mac

# 4. Test connection
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "SELECT 1;"
```

### ❌ Error: "password authentication failed"

```bash
# Credentials are HARDCODED in development:
# Username: contextforge
# Password: contextforge

# Test login manually
docker exec -it taskman-postgres psql -U contextforge -d taskman_v2

# If fails, check container environment variables
docker inspect taskman-postgres | grep -A 5 "Env"
```

### ❌ Error: "database does not exist"

```bash
# List available databases
docker exec taskman-postgres psql -U contextforge -d postgres -c "\l"

# Expected databases:
# - taskman_v2 (port 5434)
# - contextforge (port 5433)
# - sacred_context (port 5432)

# If missing, check docker-compose.yml for initialization
```

### ❌ Container not running

```bash
# Quick restart script
pwsh -File scripts/Restart-Docker.ps1

# Or manual restart
docker-compose down
docker-compose up -d taskman-postgres

# Verify healthy
docker ps --filter name=taskman-postgres --format "table {{.Names}}\t{{.Status}}"
```

---

## 📊 Database Schema (9 Tables)

```
taskman_v2
├── tasks            (9 rows)  - Core task management
├── sprints          (0 rows)  - Sprint planning
├── projects         (0 rows)  - Project hierarchy
├── tags             (0 rows)  - Task tagging
├── task_tags        (0 rows)  - Many-to-many task↔tag
├── comments         (0 rows)  - Task comments
├── attachments      (0 rows)  - File attachments
├── time_entries     (0 rows)  - Time tracking
└── audit_log        (0 rows)  - Change history
```

**Schema Details**: See `docs/AGENT-DATABASE-ACCESS.md` Section 8

---

## 🔒 Security Notes

- **Development Only**: Hardcoded credentials (contextforge/contextforge)
- **Production**: Use environment variables or secret managers
- **Network**: Containers bound to localhost only
- **Backups**: Configure pg_dump for production data

**Full Security Review**: See [docs/DATABASE-SECURITY-REVIEW.md](DATABASE-SECURITY-REVIEW.md)

---

## 📈 Performance Benchmarks

| Method | P50 Latency | P95 Latency | Overhead | Recommended For |
|--------|-------------|-------------|----------|-----------------|
| Python Direct | 162ms | 168ms | Baseline | Automation, scripts |
| Docker Exec | 208ms | 223ms | +33% | Ad-hoc queries, debugging |
| ~~MCP Server~~ | ~~185-230ms~~ | ~~193-243ms~~ | ~~+15-45%~~ | ❌ Deprecated (too complex) |

**Full Analysis**: See [docs/DATABASE-PERFORMANCE-REPORT.md](DATABASE-PERFORMANCE-REPORT.md)

---

## 📚 Related Documentation

- **Comprehensive Guide**: [docs/AGENT-DATABASE-ACCESS.md](AGENT-DATABASE-ACCESS.md) (500+ lines)
- **Performance Analysis**: [docs/DATABASE-PERFORMANCE-REPORT.md](DATABASE-PERFORMANCE-REPORT.md)
- **Security Review**: [docs/DATABASE-SECURITY-REVIEW.md](DATABASE-SECURITY-REVIEW.md)
- **Production Deployment**: [docs/PRODUCTION-DEPLOYMENT-SECURITY.md](PRODUCTION-DEPLOYMENT-SECURITY.md)
- **Agent Examples**: [AGENTS.md](../AGENTS.md#database-access)

---

## 💡 Tips & Best Practices

### For AI Agents
- Use `docker exec` for quick queries (no setup needed)
- Wrap queries in `try/catch` for error handling
- Always verify connection before running queries
- Use `LIMIT` clauses to prevent overwhelming output

### For Developers
- Use Python direct connection for better performance
- Enable query logging in development for debugging
- Use transactions for multi-statement operations
- Test queries on development database first

### For DevOps
- Monitor container health with `docker ps`
- Set up automated backups with `pg_dump`
- Review logs with `docker logs taskman-postgres`
- Use volume mounts for data persistence

---

**Quick Help**: For issues not listed here, see [Troubleshooting Flowchart](DATABASE-TROUBLESHOOTING-FLOWCHART.md) or consult [docs/AGENT-DATABASE-ACCESS.md](AGENT-DATABASE-ACCESS.md).
