# 05 – Database Design & Implementation

**Status**: Complete
**Version**: 2.0
**Last Updated**: 2025-11-11
**Related**: [02-Architecture](02-Architecture.md) | [04-Desktop-Application-Architecture](04-Desktop-Application-Architecture.md) | [09-Development-Guidelines](09-Development-Guidelines.md) | [14-Deployment-Operations](14-Deployment-Operations.md)

---

## Overview

ContextForge implements a **three-database architecture** with clear separation of concerns:
- **PostgreSQL** - Primary task management authority (TaskMan-v2)
- **DuckDB** - Analytics and velocity tracking
- **SQLite** - Legacy tracker data and supplementary context

This design balances **performance, scalability, and specialized capabilities** while maintaining data integrity through the Database Authority Principle.

---

## Access Methods & Tools

**Quick Access**: See [DATABASE-QUICK-REFERENCE.md](DATABASE-QUICK-REFERENCE.md) for immediate usage.

### Helper Scripts

| Script | Purpose | Performance |
|--------|---------|-------------|
| `scripts/db_auth.py` | Python credential helper | 168ms P95 (fastest) |
| `scripts/Get-DatabaseCredentials.ps1` | PowerShell credential helper | Cross-platform |
| `scripts/Benchmark-DatabaseAccess.ps1` | Performance benchmarking | Statistical analysis |

**Features**:
- Environment variable support (`PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE`)
- Backward compatible with dev defaults
- Production-ready with proper credential management

### Comprehensive Documentation

**Primary References**:
- [AGENT-DATABASE-ACCESS.md](AGENT-DATABASE-ACCESS.md) - AI agent guide (500+ lines)
- [DATABASE-EXAMPLE-QUERIES.md](DATABASE-EXAMPLE-QUERIES.md) - 30+ tested SQL examples
- [DATABASE-TROUBLESHOOTING-FLOWCHART.md](DATABASE-TROUBLESHOOTING-FLOWCHART.md) - Decision tree diagrams

**Security & Production**:
- [../SECURITY-REVIEW-DATABASE-ACCESS.md](../SECURITY-REVIEW-DATABASE-ACCESS.md) - 9 security findings
- [PRODUCTION-DATABASE-DEPLOYMENT.md](PRODUCTION-DATABASE-DEPLOYMENT.md) - Production deployment guide
- [DATABASE-PERFORMANCE-ANALYSIS.md](DATABASE-PERFORMANCE-ANALYSIS.md) - Benchmark results

**Agent Instructions**: Auto-activate on keywords: `database*`, `db*`, `postgres*`, `sql*`, `query*`

See [../.github/instructions/database.instructions.md](../.github/instructions/database.instructions.md) for AI agent auto-activation.

---

## Database Architecture

### Storage Model

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│         (dbcli, cf_cli, TaskMan-v2 Frontend)           │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │   DuckDB     │ │   SQLite     │
│  (PRIMARY)   │ │  (Analytics) │ │   (Legacy)   │
└──────────────┘ └──────────────┘ └──────────────┘
    Tasks              Velocity        Trackers
    Sprints           Metrics         Context
    Projects          Baseline        Logs
    Users             Performance
```

### Database Authority Principle

From [02-Architecture](02-Architecture.md):

- **PostgreSQL** (`172.25.14.122:5432/taskman_v2`) is **primary task management authority**
- **SQLite** (`db/trackers.sqlite`) maintains legacy tracker data and supplementary context
- **DuckDB** (`db/velocity.duckdb`) for analytics, no authoritative state
- Runtime CSV mutation **blocked** (`direct_csv_access_blocked`)

---

## PostgreSQL Schema (Primary Authority)

### Connection Configuration

```python
# TaskMan-v2/backend-api/config.py
class Settings(BaseSettings):
    database_url: str = "postgresql://contextforge:contextforge@172.25.14.122:5432/taskman_v2"
    database_echo: bool = False  # Set True for SQL logging

settings = Settings()
```

### Core Tables

#### Tasks Table (64 Fields)

**Purpose**: Primary task management with ContextForge 13D + Sacred Geometry

```sql
CREATE TABLE tasks (
    -- Core Identity (5 fields)
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) DEFAULT 'feature',

    -- Status & State (7 fields)
    status VARCHAR(20) DEFAULT 'new',  -- new, pending, in_progress, completed, blocked, cancelled
    priority VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    severity VARCHAR(20),
    health VARCHAR(20),
    risk_level VARCHAR(20),
    complexity VARCHAR(20),
    effort_estimate VARCHAR(50),

    -- Relationships (6 fields)
    parent_task_id VARCHAR(50),
    epic_id VARCHAR(50),
    sprint_id VARCHAR(50),
    project_id VARCHAR(50),
    dependencies JSONB,
    related_tasks JSONB,

    -- People (4 fields)
    assignee VARCHAR(100),
    created_by VARCHAR(100),
    reporter VARCHAR(100),
    stakeholders JSONB,

    -- Temporal (8 fields)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    start_date TIMESTAMP WITH TIME ZONE,
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_hours NUMERIC(10, 2),
    actual_hours NUMERIC(10, 2),
    remaining_hours NUMERIC(10, 2),

    -- Business Context (8 fields)
    business_value TEXT,
    roi_score NUMERIC(5, 4),
    customer_impact TEXT,
    strategic_alignment TEXT,
    motivational_context TEXT,
    success_criteria TEXT,
    acceptance_criteria TEXT,
    definition_of_done TEXT,

    -- Technical (10 fields)
    technical_scope TEXT,
    integration_points JSONB,
    deployment_env VARCHAR(50),
    service_topology TEXT,
    performance_targets TEXT,
    algorithm_notes TEXT,
    data_structures TEXT,
    tech_debt_score NUMERIC(5, 4),
    refactor_candidate BOOLEAN DEFAULT FALSE,
    deprecation_status VARCHAR(50),

    -- Quality (8 fields)
    test_coverage NUMERIC(5, 2),
    security_audit_status VARCHAR(50),
    accessibility_compliant BOOLEAN,
    evidence_bundle_hash VARCHAR(64),
    validation_status VARCHAR(50),
    stability_score NUMERIC(5, 4),
    completeness_pct NUMERIC(5, 2),
    quality_gate_status VARCHAR(50),

    -- COF Dimensions (8 fields)
    cof_motivational TEXT,
    cof_relational TEXT,
    cof_situational TEXT,
    cof_narrative TEXT,
    cof_sacred_geometry VARCHAR(50),  -- Triangle, Circle, Spiral, GoldenRatio, Fractal
    cof_temporal TEXT,
    cof_spatial TEXT,
    cof_holistic TEXT,

    -- Indexes
    CONSTRAINT fk_parent FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id) ON DELETE SET NULL,
    CONSTRAINT fk_sprint FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id) ON DELETE SET NULL,
    CONSTRAINT fk_project FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Performance Indexes
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assignee ON tasks(assignee);
CREATE INDEX idx_tasks_sprint ON tasks(sprint_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE due_date IS NOT NULL;
CREATE INDEX idx_tasks_sacred_geometry ON tasks(cof_sacred_geometry);

-- GIN index for JSONB columns (efficient JSON queries)
CREATE INDEX idx_tasks_dependencies ON tasks USING GIN (dependencies);
CREATE INDEX idx_tasks_integration_points ON tasks USING GIN (integration_points);
```

#### Sprints Table

```sql
CREATE TABLE sprints (
    id SERIAL PRIMARY KEY,
    sprint_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    goal TEXT,
    start_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'planned',  -- planned, active, completed, cancelled
    velocity NUMERIC(10, 2),
    capacity_hours NUMERIC(10, 2),

    -- COF/Sacred Geometry
    geometry_shape VARCHAR(20),  -- Spiral for iteration
    cof_dimensions JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sprints_status ON sprints(status);
CREATE INDEX idx_sprints_dates ON sprints(start_date, end_date);
```

#### Projects Table

```sql
CREATE TABLE projects (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',  -- planned, active, completed, archived

    -- Ownership
    owner VARCHAR(100),
    team_members JSONB,
    tags JSONB,

    -- Sacred Geometry
    geometry_shape VARCHAR(20),
    shape_stage VARCHAR(20),
    geometry_metadata JSONB,

    -- Quality Metrics
    resonance_health VARCHAR(20),
    coherence_score NUMERIC(5, 4),
    sme_confidence NUMERIC(5, 4),

    -- COF Dimensions
    cof_dimensions JSONB,

    -- UCL Compliance
    ucl_compliance JSONB,

    -- Work Codex Alignment
    codex_alignment JSONB,

    -- Planning
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_geometry ON projects(geometry_shape);
```

#### Users Table (Authentication)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    roles JSONB DEFAULT '["developer"]',  -- admin, developer, viewer, guest
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

### Database-Agnostic Design

The models support both PostgreSQL and SQLite through runtime dialect detection:

```python
# TaskMan-v2/backend-api/models.py
def get_array_type():
    """Get appropriate array type based on database dialect"""
    from database import engine

    if engine.dialect.name == "postgresql":
        from sqlalchemy.dialects.postgresql import ARRAY
        return ARRAY(String)
    else:
        # SQLite: store arrays as JSON text
        return Text

# Usage in models
class Task(Base):
    __tablename__ = "tasks"

    # PostgreSQL: ARRAY, SQLite: TEXT with JSON
    dependencies = Column(get_array_type(), nullable=True)
```

---

## Alembic Migrations

### Migration Strategy

**Additive-Only Migrations**:
- New columns appended (never removed)
- Default values provided for backward compatibility
- Sentinel checks prevent silent drift

### Directory Structure

```
TaskMan-v2/backend-api/
├── alembic/
│   ├── versions/
│   │   ├── 20251015_64_field_baseline.py
│   │   ├── 48b01bf7ee65_add_new_and_pending_to_task_status.py
│   │   ├── 4de471a82333_align_task_model_with_64_field_.py
│   │   ├── 84456d47e6aa_add_contextforge_extended_project_schema.py
│   │   └── add_users_table_for_authentication.py
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
└── models.py
```

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add COF dimensions to tasks"

# Review generated migration
cat alembic/versions/xxxxx_add_cof_dimensions_to_tasks.py

# Apply migration (staging)
alembic upgrade head

# Rollback if needed
alembic downgrade -1

# View migration history
alembic history --verbose

# Check current version
alembic current
```

### Example Migration

```python
# alembic/versions/xxxxx_add_cof_dimensions.py
"""Add COF dimensions to tasks

Revision ID: xxxxx
Revises: yyyyy
Create Date: 2025-11-11

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'xxxxx'
down_revision = 'yyyyy'

def upgrade():
    # Add COF dimension columns
    op.add_column('tasks', sa.Column('cof_motivational', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('cof_relational', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('cof_situational', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('cof_sacred_geometry', sa.String(50), nullable=True))

    # Add index for sacred geometry
    op.create_index('idx_tasks_sacred_geometry', 'tasks', ['cof_sacred_geometry'])

    # Emit evidence
    print("Migration: Added COF dimensions to tasks table")

def downgrade():
    op.drop_index('idx_tasks_sacred_geometry', 'tasks')
    op.drop_column('tasks', 'cof_sacred_geometry')
    op.drop_column('tasks', 'cof_situational')
    op.drop_column('tasks', 'cof_relational')
    op.drop_column('tasks', 'cof_motivational')
```

### Migration Testing

```python
# tests/migrations/test_alembic_downgrade.py
def test_migration_roundtrip():
    """Test migration up and down."""
    # Get current version
    current = alembic_current_version()

    # Downgrade one version
    subprocess.run(["alembic", "downgrade", "-1"], check=True)

    # Upgrade back
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    # Verify schema intact
    assert alembic_current_version() == current
```

---

## DuckDB Analytics

### Schema

```sql
-- velocity_metrics table
CREATE TABLE velocity_metrics (
    session_id VARCHAR,
    task_id VARCHAR,
    task_title VARCHAR,
    sprint_id VARCHAR,
    story_points DOUBLE,
    actual_hours DOUBLE,
    completed_at TIMESTAMP,
    complexity VARCHAR,
    velocity_ratio DOUBLE  -- hours per story point
);

-- Baseline metrics
CREATE TABLE velocity_baseline (
    metric_name VARCHAR PRIMARY KEY,
    baseline_value DOUBLE,
    calculated_at TIMESTAMP,
    sample_size INTEGER
);

-- Insert baseline
INSERT INTO velocity_baseline VALUES
('hours_per_point', 0.23, NOW(), 150);
```

### Analytics Queries

```sql
-- Sprint velocity
SELECT
    sprint_id,
    COUNT(*) as completed_tasks,
    SUM(story_points) as total_points,
    SUM(actual_hours) as total_hours,
    SUM(actual_hours) / SUM(story_points) as hours_per_point
FROM velocity_metrics
WHERE sprint_id = 'SPRINT-001'
GROUP BY sprint_id;

-- Complexity analysis
SELECT
    complexity,
    AVG(velocity_ratio) as avg_hours_per_point,
    STDDEV(velocity_ratio) as stddev
FROM velocity_metrics
GROUP BY complexity
ORDER BY avg_hours_per_point DESC;

-- Performance trends
SELECT
    DATE_TRUNC('week', completed_at) as week,
    AVG(velocity_ratio) as avg_velocity,
    COUNT(*) as task_count
FROM velocity_metrics
GROUP BY week
ORDER BY week DESC
LIMIT 12;
```

### Python Integration

```python
import duckdb

def record_velocity(task_id: str, hours: float, points: int, sprint_id: str):
    """Record task velocity in DuckDB."""
    conn = duckdb.connect("db/velocity.duckdb")

    conn.execute("""
        INSERT INTO velocity_metrics
        (task_id, actual_hours, story_points, sprint_id, completed_at, velocity_ratio)
        VALUES (?, ?, ?, ?, NOW(), ?)
    """, [task_id, hours, points, sprint_id, hours/points if points > 0 else 0])

    conn.close()
    logger.info("velocity_recorded", task_id=task_id, hours=hours, points=points)

def get_sprint_velocity(sprint_id: str) -> dict:
    """Get velocity metrics for sprint."""
    conn = duckdb.connect("db/velocity.duckdb")

    result = conn.execute("""
        SELECT
            COUNT(*) as task_count,
            SUM(story_points) as total_points,
            SUM(actual_hours) as total_hours,
            AVG(velocity_ratio) as avg_hours_per_point
        FROM velocity_metrics
        WHERE sprint_id = ?
    """, [sprint_id]).fetchone()

    conn.close()

    return {
        "task_count": result[0],
        "total_points": result[1],
        "total_hours": result[2],
        "avg_hours_per_point": result[3]
    }
```

---

## SQLite Legacy Database

### Purpose

- Legacy tracker data from CSV migration
- Supplementary context objects
- Local development/testing

### Schema

```sql
-- Legacy tasks (simplified)
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'new',
    priority TEXT DEFAULT 'medium',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Context objects
CREATE TABLE context_objects (
    kind TEXT NOT NULL,
    object_id TEXT NOT NULL,
    status TEXT DEFAULT 'placeholder',  -- placeholder, draft, complete
    data TEXT,  -- JSON blob
    PRIMARY KEY (kind, object_id)
);

-- Session logs
CREATE TABLE session_logs (
    session_id TEXT PRIMARY KEY,
    started_at TEXT,
    ended_at TEXT,
    events TEXT  -- JSON array of events
);
```

### When to Use SQLite

✅ **Use SQLite for**:
- Local development (no PostgreSQL required)
- Unit tests (fast, isolated)
- Legacy data access
- Offline operations

❌ **Don't use SQLite for**:
- Production TaskMan-v2 data (use PostgreSQL)
- Multi-user environments
- High-concurrency writes

---

## Connection Pooling

### PostgreSQL Pool Configuration

```python
# TaskMan-v2/backend-api/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.database_url,
    pool_size=20,              # Max connections in pool
    max_overflow=10,           # Extra connections during spikes
    pool_pre_ping=True,        # Verify connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=settings.database_echo  # SQL logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency injection
def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## Performance Optimization

### Query Optimization

**N+1 Query Prevention**:
```python
from sqlalchemy.orm import joinedload

# ❌ BAD: N+1 queries
tasks = db.query(Task).all()
for task in tasks:
    print(task.sprint.title)  # Separate query for each task!

# ✅ GOOD: Eager loading
tasks = db.query(Task).options(
    joinedload(Task.sprint),
    joinedload(Task.assignee)
).all()
for task in tasks:
    print(task.sprint.title)  # No extra queries
```

**Batch Inserts**:
```python
# ✅ Bulk insert
db.bulk_insert_mappings(Task, [
    {"task_id": "TASK-001", "title": "Task 1"},
    {"task_id": "TASK-002", "title": "Task 2"},
    # ...
])
db.commit()
```

### Index Strategy

**Query Analysis**:
```sql
-- Enable query timing
\timing on

-- Explain query plan
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE status = 'in_progress'
AND assignee = 'user@example.com'
ORDER BY created_at DESC
LIMIT 50;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'tasks'
ORDER BY idx_scan DESC;
```

**Composite Indexes** (for common query patterns):
```sql
-- Frequently queried together
CREATE INDEX idx_tasks_status_assignee ON tasks(status, assignee);
CREATE INDEX idx_tasks_sprint_status ON tasks(sprint_id, status);
```

---

## Backup & Restore

### PostgreSQL Backup

```bash
#!/bin/bash
# scripts/backup-postgres.sh

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/backups/postgres"
DB_NAME="taskman_v2"

# Full backup
pg_dump -U contextforge -h 172.25.14.122 -d $DB_NAME \
  -F c \
  -f "$BACKUP_DIR/taskman_$TIMESTAMP.dump"

# Compressed SQL backup
pg_dump -U contextforge -h 172.25.14.122 -d $DB_NAME \
  | gzip > "$BACKUP_DIR/taskman_$TIMESTAMP.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/taskman_$TIMESTAMP.dump" \
  s3://contextforge-backups/postgres/

# Retain last 30 days
find $BACKUP_DIR -name "taskman_*.dump" -mtime +30 -delete

# Emit evidence
python -c "from python.services.unified_logger import logger; \
logger.info('database_backup_completed', timestamp='$TIMESTAMP', size_mb=$(du -m $BACKUP_DIR/taskman_$TIMESTAMP.dump | cut -f1))"
```

### PostgreSQL Restore

```bash
#!/bin/bash
# scripts/restore-postgres.sh

BACKUP_FILE=$1

# Download from S3
aws s3 cp "s3://contextforge-backups/postgres/$BACKUP_FILE" /tmp/

# Restore custom format
pg_restore -U contextforge -h 172.25.14.122 -d taskman_v2 \
  --clean --if-exists \
  "/tmp/$BACKUP_FILE"

# Or restore SQL format
gunzip < "/tmp/$BACKUP_FILE" | \
  psql -U contextforge -h 172.25.14.122 -d taskman_v2

# Verify
psql -U contextforge -h 172.25.14.122 -d taskman_v2 \
  -c "SELECT COUNT(*) FROM tasks;"
```

### Automated Backup Schedule

```yaml
# .github/workflows/db-backup.yml
name: Database Backup

on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Backup PostgreSQL
        env:
          PGPASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
        run: |
          pg_dump -U contextforge -h 172.25.14.122 -d taskman_v2 \
            | gzip > backup_$(date +%Y%m%d).sql.gz

      - name: Upload to S3
        run: |
          aws s3 cp backup_$(date +%Y%m%d).sql.gz \
            s3://contextforge-backups/postgres/
```

---

## Validation Rules

### Data Integrity Constraints

```python
# TaskMan-v2/backend-api/models.py
from sqlalchemy import CheckConstraint

class Task(Base):
    # ...

    __table_args__ = (
        # Ensure estimated_hours is positive
        CheckConstraint('estimated_hours IS NULL OR estimated_hours > 0', name='chk_estimated_hours_positive'),

        # Ensure due_date is after start_date
        CheckConstraint('due_date IS NULL OR start_date IS NULL OR due_date >= start_date', name='chk_dates_logical'),

        # Ensure completeness_pct is 0-100
        CheckConstraint('completeness_pct IS NULL OR (completeness_pct >= 0 AND completeness_pct <= 100)', name='chk_completeness_range'),
    )
```

### Application-Level Validation

```python
# TaskMan-v2/backend-api/schemas.py
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    status: str = Field(default='new', pattern='^(new|pending|in_progress|completed|blocked|cancelled)$')
    priority: str = Field(default='medium', pattern='^(low|medium|high|critical)$')
    estimated_hours: Optional[float] = Field(None, gt=0)

    @validator('sprint_id')
    def sprint_must_exist(cls, v, values):
        """Validate sprint exists if provided."""
        if v:
            # Check sprint exists in database
            pass
        return v
```

---

## CLI Interface

### dbcli Commands

```bash
# Task operations
python dbcli.py task create "Implement JWT auth" --priority high --sprint SPRINT-001
python dbcli.py task list --json
python dbcli.py task update TASK-001 --status in_progress
python dbcli.py task complete TASK-001

# Sprint operations
python dbcli.py sprint create "Q1 2025 Sprint" --start-date 2025-01-01 --end-date 2025-03-31
python dbcli.py sprint status SPRINT-001 --json

# Velocity operations
python dbcli.py velocity record --task-id TASK-001 --hours 2.5 --story-points 3
python dbcli.py velocity metrics --json

# Database status
python dbcli.py status migration  # Check Alembic status
python dbcli.py status duckdb     # Check DuckDB analytics
```

---

## Cross References

### Foundation Documents

- [02-Architecture.md](02-Architecture.md) - Storage layer, Database Authority Principle
- [04-Desktop-Application-Architecture.md](04-Desktop-Application-Architecture.md) - TaskMan-v2 backend integration
- [09-Development-Guidelines.md](09-Development-Guidelines.md) - Database authority enforcement
- [14-Deployment-Operations.md](14-Deployment-Operations.md) - Backup/restore, migration CI/CD

### Authoritative Source

- [docs/Codex/ContextForge Work Codex.md](Codex/ContextForge%20Work%20Codex%20—%20Professional%20Principles%20with%20Philosophy.md) - **PRIMARY SOURCE**

### Implementation Details

- [TaskMan-v2/backend-api/models.py](../TaskMan-v2/backend-api/models.py) - SQLAlchemy models
- [TaskMan-v2/backend-api/alembic/](../TaskMan-v2/backend-api/alembic/) - Migration scripts
- [TaskMan-v2/backend-api/database.py](../TaskMan-v2/backend-api/database.py) - Connection pooling

---

**Document Status**: Complete ✅
**Authoritative**: Yes (integrated with Codex)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Data Engineering Team

---

*"Fix the root, not the symptom. Database schema is the root of data integrity."*
