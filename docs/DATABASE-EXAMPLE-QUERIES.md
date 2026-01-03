# Database Example Queries Library

**Version**: 1.0 | **Date**: 2025-12-29 | **Database**: taskman_v2 (PostgreSQL)

---

## 📋 Table of Contents

1. [Basic CRUD Operations](#basic-crud-operations)
2. [Filtering & Searching](#filtering--searching)
3. [Aggregations & Analytics](#aggregations--analytics)
4. [Joins & Relationships](#joins--relationships)
5. [Schema Inspection](#schema-inspection)
6. [Administrative Queries](#administrative-queries)

---

## Basic CRUD Operations

### Create (INSERT)

```sql
-- Insert a single task
INSERT INTO tasks (id, title, description, status, priority, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'Implement user authentication',
    'Add JWT-based authentication to API endpoints',
    'new',
    4,
    NOW(),
    NOW()
)
RETURNING id, title, status;

/* Expected Output:
                  id                  |           title            | status
--------------------------------------+---------------------------+--------
 a1b2c3d4-e5f6-4789-a012-3456789abcde | Implement user authentication | new
(1 row)
*/
```

```sql
-- Insert multiple tasks at once
INSERT INTO tasks (id, title, status, priority, created_at, updated_at)
VALUES
    (gen_random_uuid(), 'Write API tests', 'new', 3, NOW(), NOW()),
    (gen_random_uuid(), 'Update documentation', 'new', 2, NOW(), NOW()),
    (gen_random_uuid(), 'Code review PR #42', 'in_progress', 4, NOW(), NOW())
RETURNING id, title, status;

/* Expected Output:
                  id                  |       title        |   status
--------------------------------------+-------------------+-----------
 b2c3d4e5-f6a7-4890-b123-456789abcdef | Write API tests    | new
 c3d4e5f6-a7b8-4901-c234-56789abcdef0 | Update documentation | new
 d4e5f6a7-b8c9-4012-d345-6789abcdef01 | Code review PR #42 | in_progress
(3 rows)
*/
```

### Read (SELECT)

```sql
-- Get all tasks
SELECT id, title, status, priority
FROM tasks
ORDER BY priority DESC, created_at ASC;

/* Expected Output (current database):
                  id                  |           title            | status | priority
--------------------------------------+---------------------------+--------+----------
 123e4567-e89b-12d3-a456-426614174001 | High priority task        | new    |        5
 123e4567-e89b-12d3-a456-426614174002 | Medium priority task      | new    |        3
 123e4567-e89b-12d3-a456-426614174003 | Low priority task         | done   |        1
(9 rows)
*/
```

```sql
-- Get a specific task by ID
SELECT * FROM tasks
WHERE id = '123e4567-e89b-12d3-a456-426614174000';

/* Expected Output:
                  id                  |     title      | description | status | priority |         created_at         |         updated_at
--------------------------------------+----------------+-------------+--------+----------+----------------------------+----------------------------
 123e4567-e89b-12d3-a456-426614174000 | Example Task 1 | Details...  | new    |        3 | 2025-12-29 10:00:00.000000 | 2025-12-29 10:00:00.000000
(1 row)
*/
```

### Update (UPDATE)

```sql
-- Update task status
UPDATE tasks
SET
    status = 'in_progress',
    updated_at = NOW()
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
RETURNING id, title, status, updated_at;

/* Expected Output:
                  id                  |     title      |   status    |         updated_at
--------------------------------------+----------------+-------------+----------------------------
 123e4567-e89b-12d3-a456-426614174000 | Example Task 1 | in_progress | 2025-12-29 14:23:15.123456
(1 row)
*/
```

```sql
-- Update multiple fields
UPDATE tasks
SET
    status = 'completed',
    priority = 5,
    description = 'Completed with additional notes',
    updated_at = NOW()
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
RETURNING *;
```

### Delete (DELETE)

```sql
-- Delete a specific task (use with caution!)
DELETE FROM tasks
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
RETURNING id, title, status;

/* Expected Output:
                  id                  |     title      | status
--------------------------------------+----------------+--------
 123e4567-e89b-12d3-a456-426614174000 | Example Task 1 | completed
(1 row)
*/
```

```sql
-- Delete with safety checks (recommended)
DELETE FROM tasks
WHERE status = 'done'
  AND updated_at < NOW() - INTERVAL '90 days'
RETURNING id, title, updated_at;

/* Expected Output:
                  id                  |     title      |         updated_at
--------------------------------------+----------------+----------------------------
 a1b2c3d4-e5f6-4789-a012-3456789abcde | Old task 1     | 2025-09-15 10:00:00.000000
 b2c3d4e5-f6a7-4890-b123-456789abcdef | Old task 2     | 2025-09-20 11:30:00.000000
(2 rows)
*/
```

---

## Filtering & Searching

### Simple Filters

```sql
-- Tasks by status
SELECT id, title, status, priority
FROM tasks
WHERE status = 'new'
ORDER BY priority DESC;

/* Expected Output (current database):
                  id                  |        title         | status | priority
--------------------------------------+---------------------+--------+----------
 (8 rows showing all 'new' tasks ordered by priority)
*/
```

```sql
-- High priority tasks (priority >= 4)
SELECT id, title, priority, status
FROM tasks
WHERE priority >= 4
ORDER BY created_at DESC;
```

```sql
-- Tasks created in the last 7 days
SELECT id, title, created_at
FROM tasks
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### Complex Filters (Multiple Conditions)

```sql
-- Active high-priority tasks
SELECT id, title, status, priority
FROM tasks
WHERE status IN ('new', 'in_progress')
  AND priority >= 3
ORDER BY priority DESC, created_at ASC;
```

```sql
-- Tasks with text search in title or description
SELECT id, title, description, status
FROM tasks
WHERE title ILIKE '%authentication%'
   OR description ILIKE '%authentication%';

/* Expected Output:
                  id                  |           title            |          description           | status
--------------------------------------+---------------------------+-------------------------------+--------
 a1b2c3d4-e5f6-4789-a012-3456789abcde | Implement user authentication | Add JWT-based authentication... | new
(1 row)
*/
```

### Pagination

```sql
-- First page (10 items per page)
SELECT id, title, status, priority
FROM tasks
ORDER BY created_at DESC
LIMIT 10 OFFSET 0;

-- Second page
SELECT id, title, status, priority
FROM tasks
ORDER BY created_at DESC
LIMIT 10 OFFSET 10;

-- Calculate total pages
SELECT CEIL(COUNT(*)::DECIMAL / 10) AS total_pages
FROM tasks;

/* Expected Output:
 total_pages
-------------
           1
(1 row)
*/
```

---

## Aggregations & Analytics

### Count & Sum

```sql
-- Count all tasks
SELECT COUNT(*) AS total_tasks FROM tasks;

/* Expected Output:
 total_tasks
-------------
           9
(1 row)
*/
```

```sql
-- Count tasks by status
SELECT
    status,
    COUNT(*) AS task_count
FROM tasks
GROUP BY status
ORDER BY task_count DESC;

/* Expected Output:
 status | task_count
--------+------------
 new    |          8
 done   |          1
(2 rows)
*/
```

```sql
-- Count tasks by priority level
SELECT
    priority,
    COUNT(*) AS task_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM tasks
GROUP BY priority
ORDER BY priority DESC;

/* Expected Output:
 priority | task_count | percentage
----------+------------+------------
        5 |          2 |      22.22
        4 |          3 |      33.33
        3 |          3 |      33.33
        2 |          1 |      11.11
(4 rows)
*/
```

### Average & Statistics

```sql
-- Average priority by status
SELECT
    status,
    COUNT(*) AS task_count,
    AVG(priority) AS avg_priority,
    MIN(priority) AS min_priority,
    MAX(priority) AS max_priority
FROM tasks
GROUP BY status;

/* Expected Output:
 status | task_count | avg_priority | min_priority | max_priority
--------+------------+--------------+--------------+--------------
 new    |          8 |         3.50 |            2 |            5
 done   |          1 |         4.00 |            4 |            4
(2 rows)
*/
```

### Time-Based Analytics

```sql
-- Tasks created per day (last 30 days)
SELECT
    DATE(created_at) AS created_date,
    COUNT(*) AS tasks_created
FROM tasks
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY created_date DESC;

/* Expected Output:
 created_date | tasks_created
--------------+---------------
 2025-12-29   |             5
 2025-12-28   |             3
 2025-12-27   |             1
(3 rows)
*/
```

```sql
-- Task completion rate
SELECT
    status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM tasks
GROUP BY status;

/* Expected Output:
   status    | count | percentage
-------------+-------+------------
 new         |     8 |      88.89
 done        |     1 |      11.11
(2 rows)
*/
```

---

## Joins & Relationships

### Left Join (Tasks with Sprints)

```sql
-- Get tasks and their associated sprints
SELECT
    t.id,
    t.title,
    t.status,
    s.name AS sprint_name,
    s.start_date,
    s.end_date
FROM tasks t
LEFT JOIN sprints s ON t.sprint_id = s.id
ORDER BY t.created_at DESC
LIMIT 10;

/* Expected Output (no sprints assigned yet):
                  id                  |        title         | status | sprint_name | start_date | end_date
--------------------------------------+---------------------+--------+-------------+------------+----------
 123e4567-e89b-12d3-a456-426614174001 | Example Task 1      | new    | NULL        | NULL       | NULL
 123e4567-e89b-12d3-a456-426614174002 | Example Task 2      | new    | NULL        | NULL       | NULL
(9 rows with all NULL sprint columns)
*/
```

### Inner Join (Only Tasks in Sprints)

```sql
-- Get only tasks that are assigned to sprints
SELECT
    t.id,
    t.title,
    t.status,
    s.name AS sprint_name
FROM tasks t
INNER JOIN sprints s ON t.sprint_id = s.id;

/* Expected Output (when sprints exist):
                  id                  |        title         | status | sprint_name
--------------------------------------+---------------------+--------+-------------
 (0 rows currently - no sprint assignments)
*/
```

### Multiple Joins

```sql
-- Tasks with projects, sprints, and tag counts
SELECT
    t.id,
    t.title,
    p.name AS project_name,
    s.name AS sprint_name,
    COUNT(DISTINCT tt.tag_id) AS tag_count
FROM tasks t
LEFT JOIN projects p ON t.project_id = p.id
LEFT JOIN sprints s ON t.sprint_id = s.id
LEFT JOIN task_tags tt ON t.id = tt.task_id
GROUP BY t.id, t.title, p.name, s.name
ORDER BY t.created_at DESC;
```

### Subqueries

```sql
-- Tasks with more than average priority
SELECT id, title, priority
FROM tasks
WHERE priority > (SELECT AVG(priority) FROM tasks);

/* Expected Output:
                  id                  |        title         | priority
--------------------------------------+---------------------+----------
 123e4567-e89b-12d3-a456-426614174001 | High priority task  |        5
 123e4567-e89b-12d3-a456-426614174002 | Important task      |        4
(2 rows, assuming average is 3.5)
*/
```

---

## Schema Inspection

### List Tables

```sql
-- List all tables in the database
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

/* Expected Output:
   tablename
---------------
 attachments
 audit_log
 comments
 projects
 sprints
 tags
 task_tags
 tasks
 time_entries
(9 rows)
*/
```

### Describe Table Structure

```sql
-- Get column details for tasks table
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'tasks'
ORDER BY ordinal_position;

/* Expected Output:
  column_name   |     data_type      | character_maximum_length | is_nullable | column_default
----------------+-------------------+-------------------------+-------------+----------------
 id             | uuid              | NULL                    | NO          | gen_random_uuid()
 title          | character varying | 255                     | NO          | NULL
 description    | text              | NULL                    | YES         | NULL
 status         | character varying | 50                      | NO          | 'new'::character varying
 priority       | integer           | NULL                    | NO          | 3
 created_at     | timestamp         | NULL                    | NO          | now()
 updated_at     | timestamp         | NULL                    | NO          | now()
 sprint_id      | uuid              | NULL                    | YES         | NULL
 project_id     | uuid              | NULL                    | YES         | NULL
(9 rows)
*/
```

### Table Row Counts

```sql
-- Get row counts for all tables
SELECT
    schemaname,
    tablename,
    n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
ORDER BY n_live_tup DESC;

/* Expected Output:
 schemaname |  tablename   | row_count
------------+--------------+-----------
 public     | tasks        |         9
 public     | sprints      |         0
 public     | projects     |         0
 public     | tags         |         0
 public     | task_tags    |         0
 public     | comments     |         0
 public     | attachments  |         0
 public     | time_entries |         0
 public     | audit_log    |         0
(9 rows)
*/
```

### Indexes

```sql
-- List all indexes on tasks table
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'tasks'
ORDER BY indexname;

/* Expected Output:
        indexname        |                              indexdef
-------------------------+---------------------------------------------------------------------
 tasks_pkey              | CREATE UNIQUE INDEX tasks_pkey ON public.tasks USING btree (id)
 idx_tasks_status        | CREATE INDEX idx_tasks_status ON public.tasks USING btree (status)
 idx_tasks_priority      | CREATE INDEX idx_tasks_priority ON public.tasks USING btree (priority)
(3 rows)
*/
```

---

## Administrative Queries

### Database Size

```sql
-- Get database size
SELECT
    pg_database.datname AS database_name,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'taskman_v2';

/* Expected Output:
 database_name |  size
---------------+--------
 taskman_v2    | 8192 kB
(1 row)
*/
```

### Table Sizes

```sql
-- Get size of each table
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

/* Expected Output:
  tablename   |  size
--------------+--------
 tasks        | 16 kB
 audit_log    | 8 kB
 time_entries | 8 kB
 comments     | 8 kB
(9 rows)
*/
```

### Active Connections

```sql
-- List active connections to the database
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity
WHERE datname = 'taskman_v2';

/* Expected Output:
  pid  |   usename    | application_name | client_addr | state  |         query_start
-------+--------------+------------------+-------------+--------+----------------------------
 12345 | contextforge | psql             | NULL        | active | 2025-12-29 14:30:15.123456
(1 row)
*/
```

### Recent Activity

```sql
-- Check when tables were last accessed
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

---

## Query Templates

### Template: Filtered List with Pagination

```sql
-- Replace placeholders: {status}, {limit}, {offset}
SELECT id, title, status, priority, created_at
FROM tasks
WHERE status = 'new'  -- Replace with desired status
ORDER BY priority DESC, created_at ASC
LIMIT 10              -- Replace with page size
OFFSET 0;             -- Replace with (page_number - 1) * page_size
```

### Template: Upsert (Insert or Update)

```sql
-- Insert new task or update if ID exists
INSERT INTO tasks (id, title, status, priority, created_at, updated_at)
VALUES (
    '123e4567-e89b-12d3-a456-426614174000',  -- Replace with actual/generated UUID
    'Task Title',                              -- Replace with actual title
    'new',                                     -- Replace with actual status
    3,                                         -- Replace with actual priority
    NOW(),
    NOW()
)
ON CONFLICT (id)
DO UPDATE SET
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    priority = EXCLUDED.priority,
    updated_at = NOW()
RETURNING *;
```

### Template: Soft Delete (Mark as Deleted)

```sql
-- Add 'deleted_at' column first (if not exists)
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

-- Soft delete a task
UPDATE tasks
SET deleted_at = NOW()
WHERE id = '123e4567-e89b-12d3-a456-426614174000'
RETURNING id, title, deleted_at;

-- Query excluding deleted tasks
SELECT * FROM tasks WHERE deleted_at IS NULL;
```

---

## Running These Examples

### Option 1: Docker Exec (Quick)

```bash
# Copy any query above and run:
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "YOUR_QUERY_HERE"
```

### Option 2: Interactive Shell

```bash
# Open psql shell
docker exec -it taskman-postgres psql -U contextforge -d taskman_v2

# Paste queries directly
# Use \x for expanded display
# Use \q to exit
```

### Option 3: Python Script

```python
import psycopg2
conn = psycopg2.connect("postgresql://contextforge:contextforge@localhost:5434/taskman_v2")
cursor = conn.cursor()
cursor.execute("YOUR_QUERY_HERE")
rows = cursor.fetchall()
for row in rows:
    print(row)
cursor.close()
conn.close()
```

---

## Next Steps

- **Quick Reference**: See [DATABASE-QUICK-REFERENCE.md](DATABASE-QUICK-REFERENCE.md)
- **Troubleshooting**: See [DATABASE-TROUBLESHOOTING-FLOWCHART.md](DATABASE-TROUBLESHOOTING-FLOWCHART.md)
- **Comprehensive Guide**: See [AGENT-DATABASE-ACCESS.md](AGENT-DATABASE-ACCESS.md)
- **Performance**: See [DATABASE-PERFORMANCE-REPORT.md](DATABASE-PERFORMANCE-REPORT.md)
