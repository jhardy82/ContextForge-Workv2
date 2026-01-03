# Database Migrations Guide

> Alembic migration management for TaskMan-v2 Backend API

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Migration Commands](#migration-commands)
- [Initial Schema](#initial-schema)
- [Creating Migrations](#creating-migrations)
- [Applying Migrations](#applying-migrations)
- [Rollback Procedures](#rollback-procedures)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

TaskMan-v2 uses **Alembic** for database schema migrations with **async SQLAlchemy 2.0** support.

**Key Features:**
- ✅ Async-first migration environment
- ✅ Timestamped migration naming (YYYYMMDD_HHMM_revision_description)
- ✅ Autogenerate support for schema changes
- ✅ PostgreSQL with asyncpg driver
- ✅ UTC timezone for all timestamps
- ✅ Online and offline migration modes

**Current Schema Version:** `934f38a4fc73` (Phases and status fields)

**Migration Chain:**
1. `c7bb9a9f0570` - Initial schema (projects, sprints, tasks, action_lists)
2. `a1b2c3d4e5f6` - Add action_lists table (deferred migration)
3. `934f38a4fc73` - Add phases and status fields to all entities

---

## Quick Start

### Prerequisites

1. **PostgreSQL database running** (local or Docker)
2. **Environment variables configured** (`.env` file)
3. **Package installed** in development mode:
   ```bash
   uv pip install -e .
   ```

### First Time Setup

```bash
# 1. Verify Alembic configuration
cd TaskMan-v2/backend-api
alembic current

# 2. Create database (if not exists)
createdb taskman_dev

# 3. Apply initial migration
alembic upgrade head

# 4. Verify schema
alembic current
# Output: c7bb9a9f0570 (head)
```

---

## Migration Commands

### Check Current Version

```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Show verbose history with details
alembic history --verbose
```

### Create New Migration

```bash
# Autogenerate migration from model changes
alembic revision --autogenerate -m "Add user authentication"

# Create empty migration (manual SQL)
alembic revision -m "Add custom index"
```

**Migration File Location:**
`alembic/versions/YYYYMMDD_HHMM_<revision>_<description>.py`

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific revision
alembic upgrade c7bb9a9f0570

# Show SQL without executing (dry run)
alembic upgrade head --sql
```

### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade c7bb9a9f0570

# Downgrade to base (drop all)
alembic downgrade base

# Show SQL without executing (dry run)
alembic downgrade -1 --sql
```

---

## Initial Schema

**Migration:** `20251225_1911_c7bb9a9f0570_initial_schema.py`

Creates four tables with full ContextForge integration:

### 1. Projects Table

**Pattern:** `P-[A-Za-z0-9_-]+` (e.g., `P-TASKMAN-V2`)

| Column | Type | Description |
|--------|------|-------------|
| id | String(50) | Primary key (project ID) |
| name | String(200) | Project name |
| mission | Text | Mission statement |
| status | String(20) | Status (discovery, active, paused, closed) |
| owner | String(100) | Project owner/lead |
| okrs | JSON | Objectives and Key Results |
| roadmap | JSON | Milestones and timeline |
| observability | JSON | Health monitoring data |
| created_at | DateTime(TZ) | Creation timestamp |
| updated_at | DateTime(TZ) | Last update timestamp |

**Total Columns:** 28 fields + timestamps

**Indexes:**
- `idx_projects_status`
- `idx_projects_owner`
- `idx_projects_start_date`
- `idx_projects_created_at`
- `idx_projects_updated_at`

### 2. Sprints Table

**Pattern:** `S-[A-Za-z0-9_-]+` (e.g., `S-2025-01`)

| Column | Type | Description |
|--------|------|-------------|
| id | String(50) | Primary key (sprint ID) |
| name | String(200) | Sprint name |
| goal | Text | Sprint goal/objective |
| cadence | String(20) | Cadence (weekly, biweekly, monthly) |
| status | String(20) | Status (planned, active, closed) |
| primary_project | String(50) | FK to projects.id (CASCADE) |
| velocity_target_points | Float | Target velocity |
| ceremonies | JSON | Ceremony notes and links |
| metrics | JSON | Sprint metrics |
| observability | JSON | Health monitoring data |

**Total Columns:** 23 fields + timestamps

**Indexes:**
- `idx_sprints_status`
- `idx_sprints_primary_project`
- `idx_sprints_owner`
- `idx_sprints_start_date`
- `idx_sprints_end_date`
- `idx_sprints_project_status` (composite)
- `idx_sprints_created_at`
- `idx_sprints_updated_at`

### 3. Tasks Table (70+ Fields)

**Pattern:** `T-[A-Za-z0-9_-]+` (e.g., `T-ULOG-001`)

| Column | Type | Description |
|--------|------|-------------|
| id | String(50) | Primary key (task ID) |
| title | String(500) | Task title |
| summary | Text | Brief summary (1-2 sentences) |
| description | Text | Detailed description |
| status | String(20) | Status (new, ready, in_progress, blocked, review, done, dropped) |
| owner | String(100) | Task owner |
| assignees | JSON | List of assigned team members |
| priority | String(20) | Priority (p0=critical, p1=high, p2=medium, p3=low) |
| primary_project | String(50) | FK to projects.id (CASCADE) |
| primary_sprint | String(50) | FK to sprints.id (CASCADE) |
| acceptance_criteria | JSON | Acceptance criteria list |
| quality_gates | JSON | Quality gate results |
| verification | JSON | MPV plan and evidence |
| observability | JSON | Health monitoring data |

**Total Columns:** 42 fields + timestamps

**Indexes:**
- `idx_tasks_status`
- `idx_tasks_priority`
- `idx_tasks_owner`
- `idx_tasks_primary_project`
- `idx_tasks_primary_sprint`
- `idx_tasks_status_priority` (composite)
- `idx_tasks_project_status` (composite)
- `idx_tasks_sprint_status` (composite)
- `idx_tasks_created_at`
- `idx_tasks_updated_at`

### 4. Action Lists Table

**Pattern:** Custom ID

| Column | Type | Description |
|--------|------|-------------|
| id | String(50) | Primary key |
| title | String(255) | Action list title |
| description | Text | Detailed description |
| status | String(20) | Action list status |
| owner | String(100) | Owner (nullable) |
| items | JSON | Action items array |
| project_id | String(50) | FK to projects.id (SET NULL) |
| sprint_id | String(50) | FK to sprints.id (SET NULL) |

**Total Columns:** 17 fields + timestamps

**Indexes:**
- `idx_action_lists_owner`
- `idx_action_lists_sprint_id`
- `idx_action_lists_project_id`
- `idx_action_lists_project_status` (composite)
- `idx_action_lists_created_at`
- `idx_action_lists_updated_at`

---

## Creating Migrations

### Autogenerate from Model Changes

When you modify SQLAlchemy models:

```bash
# 1. Make changes to models in src/taskman_api/db/models/
# 2. Generate migration
alembic revision --autogenerate -m "Add email field to tasks"

# 3. Review generated migration
cat alembic/versions/YYYYMMDD_HHMM_*_add_email_field_to_tasks.py

# 4. Edit migration if needed (add data migrations, custom logic)

# 5. Apply migration
alembic upgrade head

# 6. Verify
alembic current
```

### Manual Migration

For complex operations not supported by autogenerate:

```bash
# 1. Create empty migration
alembic revision -m "Migrate task priorities"

# 2. Edit migration file manually
# Add custom upgrade() and downgrade() logic

# 3. Test upgrade
alembic upgrade head

# 4. Test downgrade
alembic downgrade -1

# 5. Reapply
alembic upgrade head
```

---

## Applying Migrations

### Development Environment

```bash
# Standard upgrade to latest
alembic upgrade head

# Verify schema matches models
alembic check
```

### Staging/Production Environment

```bash
# 1. Backup database first!
pg_dump taskman_production > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Review migration SQL (dry run)
alembic upgrade head --sql > migration.sql
cat migration.sql

# 3. Apply migration
alembic upgrade head

# 4. Verify
alembic current
psql -c "SELECT COUNT(*) FROM tasks;"

# 5. Monitor application logs for errors
```

---

## Rollback Procedures

### Emergency Rollback

If a migration causes issues in production:

```bash
# 1. Immediate rollback
alembic downgrade -1

# 2. Verify application health
curl http://localhost:8000/health/ready

# 3. Check logs for errors

# 4. Restore from backup if needed
psql taskman_production < backup_20251225_191100.sql
```

### Testing Rollback Safety

Always test downgrade before deploying:

```bash
# 1. Apply migration
alembic upgrade head

# 2. Test application

# 3. Rollback
alembic downgrade -1

# 4. Test application again

# 5. Reapply if successful
alembic upgrade head
```

---

## Best Practices

### Before Creating Migrations

1. ✅ **Review model changes** - Ensure changes are intentional
2. ✅ **Check existing migrations** - Avoid duplicates
3. ✅ **Use descriptive names** - Clear, concise migration names
4. ✅ **Test locally first** - Never create migrations in production

### Migration File Guidelines

```python
def upgrade() -> None:
    """Add email field to tasks table."""
    # 1. Use op.batch_alter_table() for SQLite compatibility (if needed)
    # 2. Add comments explaining complex operations
    # 3. Include data migrations if needed
    # 4. Handle nullable columns carefully (set defaults first)

    op.add_column('tasks', sa.Column('email', sa.String(255), nullable=True))

    # Set default value for existing rows
    op.execute("UPDATE tasks SET email = owner || '@example.com' WHERE email IS NULL")

    # Make non-nullable after setting defaults
    op.alter_column('tasks', 'email', nullable=False)

def downgrade() -> None:
    """Remove email field from tasks table."""
    # Always provide downgrade path!
    op.drop_column('tasks', 'email')
```

### Schema Changes Checklist

- [ ] Models updated in `src/taskman_api/db/models/`
- [ ] Migration created with `alembic revision --autogenerate`
- [ ] Migration reviewed and edited if needed
- [ ] Migration tested with `upgrade` and `downgrade`
- [ ] Migration tested with real data (dev database)
- [ ] Migration documented in this file (if significant)
- [ ] Indexes created for new columns (if needed)
- [ ] Foreign keys configured correctly
- [ ] Default values set appropriately
- [ ] Data migration included (if schema change affects data)

---

## Troubleshooting

### "No module named 'taskman_api'"

**Problem:** Package not installed

**Solution:**
```bash
uv pip install -e .
```

### "ValidationError: Field required"

**Problem:** Missing environment variables

**Solution:**
```bash
# Create .env file
cp .env.example .env

# Edit .env with database credentials
# Ensure APP_DATABASE__* variables are set
```

### "password authentication failed"

**Problem:** Database credentials incorrect

**Solution:**
```bash
# Verify credentials
psql -h localhost -U taskman -d taskman_dev

# Update .env with correct values
APP_DATABASE__USER=taskman
APP_DATABASE__PASSWORD=taskman_dev_password
```

### "Target database is not up to date"

**Problem:** Alembic version table out of sync

**Solution:**
```bash
# Check current version
alembic current

# Manually set version (DANGEROUS - backup first!)
alembic stamp head

# Or drop and recreate
alembic downgrade base
alembic upgrade head
```

### Autogenerate Detects No Changes

**Problem:** Models not imported in `db/base.py`

**Solution:**
```python
# In src/taskman_api/db/base.py
from .models.task import Task
from .models.project import Project
from .models.sprint import Sprint
from .models.action_list import ActionList

# Ensure Base.metadata includes all models
```

### Migration Fails with Foreign Key Constraint

**Problem:** Child records exist when trying to drop parent table

**Solution:**
```python
# In migration downgrade()
def downgrade() -> None:
    # Drop child tables first (in correct order)
    op.drop_table('tasks')           # Has FKs to projects and sprints
    op.drop_table('action_lists')    # Has FKs to projects and sprints
    op.drop_table('sprints')         # Has FK to projects
    op.drop_table('projects')        # No FKs (parent table)
```

---

## Migration History

| Version | Date | Description | Author |
|---------|------|-------------|--------|
| `c7bb9a9f0570` | 2025-12-25 | Initial schema (projects, sprints, tasks, action_lists) | ContextForge Team |
| `a1b2c3d4e5f6` | 2025-12-27 | Add action_lists table (deferred migration) | ContextForge Team |
| `934f38a4fc73` | 2025-12-28 | Add phases and status fields to all entities | ContextForge Team |

---

## Environment Configuration

### Required Environment Variables

```bash
# Database connection
APP_DATABASE__HOST=localhost
APP_DATABASE__PORT=5432
APP_DATABASE__USER=taskman
APP_DATABASE__PASSWORD=taskman_dev_password
APP_DATABASE__DATABASE=taskman_dev

# Security (minimum 32 characters each)
APP_SECRET_KEY=dev_secret_key_exactly_32_chars!!
APP_JWT_SECRET=dev_jwt_secret_exactly_32_chars!!

# Application
APP_APP_NAME=TaskMan API
APP_ENVIRONMENT=development
```

### Connection String Format

Alembic uses the async connection string:

```
postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}
```

**Example:**
```
postgresql+asyncpg://taskman:taskman_dev_password@localhost:5432/taskman_dev
```

---

## Docker Container Migrations

### Running Migrations with Docker

When using `docker-compose.taskman-v2.yml`, the database runs in a container on port 5434.

**Important:** The backend container needs all `APP_DATABASE__*` environment variables set correctly, or it will fail to start.

### Required Environment Variables for Alembic

When running Alembic from the host (outside Docker), set these environment variables:

```bash
# For local development with Docker database
export APP_DATABASE__HOST=localhost
export APP_DATABASE__PORT=5434        # Docker exposes 5434 → 5432
export APP_DATABASE__USER=contextforge
export APP_DATABASE__PASSWORD=contextforge
export APP_DATABASE__DATABASE=taskman_v2
export APP_SECRET_KEY=taskman-development-secret-key-32char
export APP_JWT_SECRET=taskman-development-jwt-key-32-chars

# Then run Alembic
cd backend-api
uv run alembic upgrade head
```

### Migration Mismatch Recovery

**Problem:** Database has a different `alembic_version` than the migration files in the codebase.

**Symptoms:**
- Backend container keeps restarting
- Error: `Can't locate revision identified by 'XXXXXX'`
- Health check returns 500

**Diagnosis:**

```bash
# Check current database version
docker exec taskman-postgres psql -U contextforge -d taskman_v2 \
  -c "SELECT version_num FROM alembic_version;"

# List available migration files
ls backend-api/alembic/versions/

# Check actual schema (compare tables/columns)
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "\dt"
docker exec taskman-postgres psql -U contextforge -d taskman_v2 -c "\d tasks"
```

**Recovery Steps:**

1. **Identify the correct version** by comparing existing database schema with migration files
2. **Stamp the database** to the matching version:
   ```bash
   docker exec taskman-postgres psql -U contextforge -d taskman_v2 \
     -c "UPDATE alembic_version SET version_num = '<correct_version>';"
   ```
3. **Apply remaining migrations** from the host:
   ```bash
   export APP_DATABASE__HOST=localhost
   export APP_DATABASE__PORT=5434
   export APP_DATABASE__USER=contextforge
   export APP_DATABASE__PASSWORD=contextforge
   export APP_DATABASE__DATABASE=taskman_v2
   export APP_SECRET_KEY=taskman-development-secret-key-32char
   export APP_JWT_SECRET=taskman-development-jwt-key-32-chars

   cd backend-api
   uv run alembic upgrade head
   ```
4. **Restart the backend container:**
   ```bash
   docker compose -f docker-compose.taskman-v2.yml restart backend
   ```
5. **Verify health:**
   ```bash
   curl http://localhost:3001/health
   ```

### Example: Recovery from c454c6908377

If database shows `c454c6908377` (orphan version) but schema matches `a1b2c3d4e5f6`:

```bash
# 1. Stamp to matching version
docker exec taskman-postgres psql -U contextforge -d taskman_v2 \
  -c "UPDATE alembic_version SET version_num = 'a1b2c3d4e5f6';"

# 2. Apply pending migrations
cd backend-api
export APP_DATABASE__HOST=localhost APP_DATABASE__PORT=5434 \
       APP_DATABASE__USER=contextforge APP_DATABASE__PASSWORD=contextforge \
       APP_DATABASE__DATABASE=taskman_v2 \
       APP_SECRET_KEY=taskman-development-secret-key-32char \
       APP_JWT_SECRET=taskman-development-jwt-key-32-chars
uv run alembic upgrade head

# 3. Restart backend
cd ..
docker compose -f docker-compose.taskman-v2.yml restart backend
```

---

## Additional Resources

- **Alembic Documentation:** https://alembic.sqlalchemy.org/
- **SQLAlchemy 2.0 Async:** https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **asyncpg Driver:** https://magicstack.github.io/asyncpg/

---

**Last Updated:** 2025-12-28
**Alembic Version:** 1.13.x
**SQLAlchemy Version:** 2.0.x
**PostgreSQL Version:** 14+
**Docker Port:** 5434 (maps to container 5432)
