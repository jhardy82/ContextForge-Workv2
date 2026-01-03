# Risk Analysis: Project CRUD Implementation for TaskMan MCP

**Document ID**: RISK-PRJ-CRUD-20251203
**Created**: 2025-12-03
**Author**: Risk Pattern Analyst Agent
**Status**: Complete
**Related**: TASKMAN-MCP-TYPESCRIPT-API-IMPLEMENTATION.md

---

## Executive Summary

This document identifies 15 potential failure modes and pitfalls for implementing FastAPI + SQLAlchemy CRUD endpoints for the `projects` table, called by TypeScript MCP server via HTTP. Each risk is categorized, scored, and paired with actionable mitigation strategies.

**Critical Risks Requiring Immediate Attention:**
1. 🔴 Datetime serialization mismatch between Python and TypeScript Zod
2. 🔴 Schema field name drift (Python snake_case vs potential camelCase)
3. 🟠 N+1 query problem without selectinload
4. 🟠 Missing connection pool configuration
5. 🟠 Cascade delete silently removing child records

---

## 1. Risk Register

### 1.1 SQLAlchemy Common Pitfalls

| Risk ID | Risk Description | Probability | Impact | Score | Category |
|---------|------------------|-------------|--------|-------|----------|
| SQL-001 | **Detached Instance Error**: Accessing ORM objects after session close | Low | High | 🟡 6 | Session |
| SQL-002 | **Uncommitted Transactions**: Forgetting commit/rollback leaves connections hung | Medium | High | 🟠 9 | Session |
| SQL-003 | **N+1 Query Problem**: Loading relationships without eager loading | High | Medium | 🟠 9 | Performance |
| SQL-004 | **Connection Pool Exhaustion**: Long requests hold connections | Medium | High | 🟠 9 | Performance |
| SQL-005 | **Transaction Isolation**: Phantom reads during pagination | Low | Medium | 🟢 4 | Consistency |

### 1.2 FastAPI + SQLAlchemy Integration

| Risk ID | Risk Description | Probability | Impact | Score | Category |
|---------|------------------|-------------|--------|-------|----------|
| FPI-001 | **Async/Sync Confusion**: Using sync methods in async routes | Medium | High | 🟠 9 | Performance |
| FPI-002 | **Response Model Validation Failure**: Pydantic rejects valid SQLAlchemy data | High | Medium | 🟠 9 | Validation |
| FPI-003 | **SQLAlchemy Exception Exposure**: Raw DB errors shown to clients | Medium | Medium | 🟡 6 | Security |
| FPI-004 | **Dependency Injection Lifecycle**: Session state leaks between handlers | Low | Medium | 🟢 4 | Session |

### 1.3 Database Operation Risks

| Risk ID | Risk Description | Probability | Impact | Score | Category |
|---------|------------------|-------------|--------|-------|----------|
| DBO-001 | **Cascade Delete Behavior**: Deleting project removes all tasks | Medium | Critical | 🔴 12 | Data Loss |
| DBO-002 | **Foreign Key Constraint Violation**: Creating task with invalid project_id | High | Medium | 🟠 9 | Validation |
| DBO-003 | **Concurrent Modification Conflict**: Lost updates from simultaneous edits | Medium | Medium | 🟡 6 | Consistency |
| DBO-004 | **Validation Gap Between Layers**: Data passes Pydantic, fails DB constraint | Medium | Medium | 🟡 6 | Validation |

### 1.4 MCP Integration Risks

| Risk ID | Risk Description | Probability | Impact | Score | Category |
|---------|------------------|-------------|--------|-------|----------|
| MCP-001 | **Datetime Serialization Mismatch**: Python isoformat vs Zod regex | High | High | 🔴 12 | Serialization |
| MCP-002 | **TypeScript-Python Schema Drift**: Field names/types don't match | High | Medium | 🟠 9 | Contract |
| MCP-003 | **UUID Serialization Failure**: Forgetting str() conversion | Medium | High | 🟠 9 | Serialization |
| MCP-004 | **404 vs Empty Result Semantics**: Different expectations for "not found" | Medium | Medium | 🟡 6 | Contract |

---

## 2. Mitigation Strategies

### 2.1 SQLAlchemy Mitigations

#### SQL-001: Detached Instance Error ✅ Already Mitigated
```python
# Current pattern in python/api/dependencies.py - GOOD
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False  # Prevents detached instance errors
)
```

#### SQL-002: Uncommitted Transactions
```python
# PATTERN: Always use explicit try/except/rollback
async def create_project(
    project: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict:
    try:
        # Create and add project
        db_project = Project(**project.model_dump())
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        return serialize_project(db_project)
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

#### SQL-003: N+1 Query Problem
```python
# PATTERN: Always use selectinload for relationships
from sqlalchemy.orm import selectinload

async def get_project_with_tasks(project_id: str, db: AsyncSession):
    stmt = (
        select(Project)
        .options(
            selectinload(Project.sprints),
            selectinload(Project.tasks),
        )
        .where(Project.id == project_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

#### SQL-004: Connection Pool Exhaustion
```python
# UPDATE python/api/dependencies.py - ADD pool settings
engine = create_async_engine(
    DATABASE_URL,
    echo=bool(os.getenv("DB_ECHO", "false").lower() == "true"),
    pool_pre_ping=True,
    pool_recycle=300,
    # ADD THESE:
    pool_size=10,           # Max persistent connections
    max_overflow=20,        # Additional connections under load
    pool_timeout=30,        # Wait time for connection
)
```

### 2.2 FastAPI + SQLAlchemy Integration Mitigations

#### FPI-001: Async/Sync Confusion
```python
# ❌ WRONG: Using sync ORM methods
project = db.query(Project).filter_by(id=project_id).first()

# ✅ CORRECT: Using async select statements
stmt = select(Project).where(Project.id == project_id)
result = await db.execute(stmt)
project = result.scalar_one_or_none()
```

#### FPI-002: Response Model Validation Failure
```python
# PATTERN: Use dict with explicit serialization, not strict response_model
@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: str, db: AsyncSession) -> dict:
    project = await fetch_project(project_id, db)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    return serialize_project(project)  # Explicit conversion

def serialize_project(project: Project) -> dict:
    """Convert SQLAlchemy model to JSON-safe dict"""
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": format_datetime(project.created_at),
        "updated_at": format_datetime(project.updated_at),
    }
```

#### FPI-003: SQLAlchemy Exception Handling
```python
# PATTERN: Exception handler at router level
from sqlalchemy.exc import IntegrityError, OperationalError

@router.post("/")
async def create_project(project: ProjectCreate, db: AsyncSession):
    try:
        # ... create logic
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        if "foreign key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Referenced entity not found")
        if "unique" in str(e).lower():
            raise HTTPException(status_code=409, detail="Project with this name already exists")
        raise HTTPException(status_code=400, detail="Data integrity error")
    except OperationalError as e:
        await db.rollback()
        raise HTTPException(status_code=503, detail="Database temporarily unavailable")
```

### 2.3 Database Operation Mitigations

#### DBO-001: Cascade Delete Behavior
```python
# PATTERN: Block delete if children exist
@router.delete("/{project_id}")
async def delete_project(project_id: str, db: AsyncSession, force: bool = False):
    # Check for children FIRST
    stmt = select(Project).options(
        selectinload(Project.sprints),
        selectinload(Project.tasks),
    ).where(Project.id == project_id)
    
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Block deletion if children exist
    child_count = len(project.sprints) + len(project.tasks)
    if child_count > 0 and not force:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Cannot delete project with existing children",
                "sprints": len(project.sprints),
                "tasks": len(project.tasks),
                "hint": "Use force=true to delete with all children, or remove children first"
            }
        )
    
    # Proceed with deletion
    await db.delete(project)
    await db.commit()
```

#### DBO-002: Foreign Key Constraint Validation
```python
# PATTERN: Pre-validate FK references
async def validate_project_exists(project_id: str, db: AsyncSession) -> bool:
    """Validate project exists before creating related entities"""
    stmt = select(Project.id).where(Project.id == project_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None

@router.post("/tasks")
async def create_task(task: TaskCreate, db: AsyncSession):
    # Validate FK BEFORE attempting insert
    if task.project_id and not await validate_project_exists(task.project_id, db):
        raise HTTPException(
            status_code=400,
            detail=f"Project {task.project_id} does not exist"
        )
    # Proceed with creation...
```

#### DBO-003: Concurrent Modification Conflict
```python
# PATTERN: Optimistic locking with version field
from sqlalchemy import Column, Integer

class Project(Base):
    # ... existing fields
    version = Column(Integer, default=1, nullable=False)

@router.put("/{project_id}")
async def update_project(
    project_id: str,
    update: ProjectUpdate,
    expected_version: int,  # Client must provide
    db: AsyncSession
):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check version
    if project.version != expected_version:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Project was modified by another request",
                "current_version": project.version,
                "your_version": expected_version
            }
        )
    
    # Apply updates
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    project.version += 1  # Increment version
    
    await db.commit()
```

### 2.4 MCP Integration Mitigations

#### MCP-001: Datetime Serialization Mismatch 🔴 CRITICAL
```python
# PROBLEM: Python datetime doesn't match TypeScript Zod regex
# Zod expects: /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?(Z)?$/
# Python produces: 2024-12-03T10:30:00.123456+00:00

# SOLUTION: Custom datetime formatter
from datetime import datetime, timezone

def format_datetime_for_mcp(dt: datetime | None) -> str | None:
    """Format datetime to match TypeScript Zod isoDateTime regex"""
    if dt is None:
        return None
    
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    
    # Format: YYYY-MM-DDTHH:MM:SS.ffffffZ (Zod-compatible)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Trim to milliseconds

# USAGE in serializer:
def serialize_project(project: Project) -> dict:
    return {
        "id": project.id,
        "name": project.name,
        "status": project.status,
        "created_at": format_datetime_for_mcp(project.created_at),
        "updated_at": format_datetime_for_mcp(project.updated_at),
    }
```

#### MCP-002: TypeScript-Python Schema Drift
```python
# SOLUTION: Create explicit mapping layer
# python/api/schemas/project_schemas.py

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    """Base schema matching TypeScript projectSchema"""
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = "planning"  # Matches TS ProjectStatus enum

class ProjectCreate(ProjectBase):
    """For POST /projects"""
    pass

class ProjectUpdate(BaseModel):
    """For PUT /projects/:id - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    """For GET responses - matches TypeScript projectRecordSchema"""
    id: str
    created_at: str  # Pre-formatted datetime string
    updated_at: str
```

#### MCP-003: UUID Serialization
```python
# PATTERN: Always convert UUID to string explicitly
def serialize_entity(entity) -> dict:
    result = {}
    for key, value in entity.__dict__.items():
        if key.startswith('_'):
            continue
        if isinstance(value, UUID):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = format_datetime_for_mcp(value)
        elif isinstance(value, Decimal):
            result[key] = float(value)
        else:
            result[key] = value
    return result
```

#### MCP-004: 404 vs Empty Result Semantics
```python
# PATTERN: Consistent semantics
# - GET /projects/{id} -> 404 if not found (single resource)
# - GET /projects -> empty array [] if no results (collection)
# - DELETE /projects/{id} -> 404 if not found (idempotent but informative)
# - POST /projects -> 201 with created resource

@router.get("/", response_model=dict)
async def list_projects(db: AsyncSession) -> dict:
    stmt = select(Project)
    result = await db.execute(stmt)
    projects = result.scalars().all()
    
    # Return empty array, NOT 404
    return {
        "projects": [serialize_project(p) for p in projects],
        "total": len(projects),
    }
```

---

## 3. Testing Recommendations

### 3.1 Unit Tests

```python
# tests/unit/test_project_serialization.py

import pytest
from datetime import datetime, timezone
from uuid import uuid4

def test_datetime_serialization_matches_zod_regex():
    """Verify datetime format matches TypeScript Zod isoDateTime"""
    from python.api.utils import format_datetime_for_mcp
    import re
    
    zod_pattern = r'^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(\.\d+)?(Z)?$'
    
    # Test various datetime scenarios
    test_cases = [
        datetime.now(timezone.utc),
        datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc),
        datetime(2024, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc),
    ]
    
    for dt in test_cases:
        formatted = format_datetime_for_mcp(dt)
        assert re.match(zod_pattern, formatted), f"Failed for {dt}: {formatted}"

def test_uuid_serialization():
    """Ensure UUID is converted to string"""
    from python.api.utils import serialize_entity
    from unittest.mock import Mock
    
    mock_project = Mock()
    mock_project.id = uuid4()
    mock_project.__dict__ = {'id': mock_project.id}
    
    result = serialize_entity(mock_project)
    assert isinstance(result['id'], str)
```

### 3.2 Integration Tests

```python
# tests/integration/test_project_crud.py

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_project_validates_schema(client: AsyncClient):
    """Verify response matches TypeScript schema expectations"""
    response = await client.post("/api/projects", json={
        "name": "Test Project",
        "description": "A test project",
    })
    
    assert response.status_code == 201
    data = response.json()
    
    # Validate schema shape
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    # Validate datetime format (Zod-compatible)
    import re
    zod_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'
    assert re.match(zod_pattern, data["created_at"])

@pytest.mark.asyncio
async def test_delete_project_with_children_blocked(client: AsyncClient, db_session):
    """Verify cascade delete protection works"""
    # Setup: Create project with task
    project_id = "P-test-001"
    # ... create project and task
    
    # Attempt delete without force flag
    response = await client.delete(f"/api/projects/{project_id}")
    
    assert response.status_code == 409
    assert "children" in response.json()["detail"]

@pytest.mark.asyncio
async def test_concurrent_update_detected(client: AsyncClient):
    """Verify optimistic locking prevents lost updates"""
    # Create project
    create_resp = await client.post("/api/projects", json={"name": "Concurrent Test"})
    project = create_resp.json()
    
    # Update 1 (should succeed)
    resp1 = await client.put(
        f"/api/projects/{project['id']}",
        json={"name": "Updated Name"},
        params={"expected_version": 1}
    )
    assert resp1.status_code == 200
    
    # Update 2 with stale version (should fail)
    resp2 = await client.put(
        f"/api/projects/{project['id']}",
        json={"name": "Conflicting Name"},
        params={"expected_version": 1}  # Stale!
    )
    assert resp2.status_code == 409

@pytest.mark.asyncio
async def test_fk_violation_returns_400(client: AsyncClient):
    """Verify FK constraint returns user-friendly error"""
    response = await client.post("/api/tasks", json={
        "title": "Orphan Task",
        "project_id": "NONEXISTENT-PROJECT"
    })
    
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]
```

### 3.3 Load Tests

```python
# tests/load/test_pool_exhaustion.py

import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.load
@pytest.mark.asyncio
async def test_connection_pool_under_load(client: AsyncClient):
    """Verify pool handles concurrent requests without exhaustion"""
    async def make_request():
        return await client.get("/api/projects")
    
    # Simulate 50 concurrent requests (exceeds default pool size of 5)
    tasks = [make_request() for _ in range(50)]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # All should succeed (pool should expand with max_overflow)
    successful = [r for r in responses if not isinstance(r, Exception)]
    assert len(successful) >= 45, "Too many pool exhaustion failures"
```

---

## 4. Code Review Checklist

### Pre-Merge Verification

| Category | Check Item | Verified |
|----------|------------|----------|
| **Session Management** | ☐ All routes use `Depends(get_db_session)` | |
| **Session Management** | ☐ All exceptions trigger `db.rollback()` | |
| **Session Management** | ☐ No sync ORM methods (`db.query()`, `db.add()` without async) | |
| **Relationships** | ☐ All relationship access uses `selectinload()` | |
| **Relationships** | ☐ No lazy loading in response serialization | |
| **Error Handling** | ☐ SQLAlchemy exceptions caught and wrapped | |
| **Error Handling** | ☐ No raw database errors in HTTP responses | |
| **Error Handling** | ☐ FK violations return 400 with helpful message | |
| **Serialization** | ☐ All datetimes use `format_datetime_for_mcp()` | |
| **Serialization** | ☐ All UUIDs converted to string | |
| **Serialization** | ☐ Response schema matches TypeScript Zod | |
| **Validation** | ☐ FK references validated before insert | |
| **Validation** | ☐ Field length limits match database constraints | |
| **Cascade** | ☐ Delete blocked if children exist (unless force) | |
| **Concurrency** | ☐ Version field updated on every mutation | |
| **Tests** | ☐ Unit tests for datetime serialization | |
| **Tests** | ☐ Integration tests for CRUD operations | |
| **Tests** | ☐ Error path tests for FK violations | |

---

## 5. Rollback Strategy

### 5.1 Feature Flag Approach

```python
# python/api/config.py
import os

FEATURE_FLAGS = {
    "use_real_project_routes": os.getenv("FF_REAL_PROJECTS", "false").lower() == "true"
}

# python/api/main.py
from .config import FEATURE_FLAGS

if FEATURE_FLAGS["use_real_project_routes"]:
    from .routes.projects import router as projects_router
else:
    from .routers.projects import router as projects_router  # Mock data version

app.include_router(projects_router)
```

### 5.2 Staged Rollout

1. **Stage 1**: Deploy with `FF_REAL_PROJECTS=false` (mock data)
2. **Stage 2**: Enable for internal testing: `FF_REAL_PROJECTS=true` on dev
3. **Stage 3**: Canary deployment to 10% of traffic
4. **Stage 4**: Full rollout if error rate < 0.1%

### 5.3 Rollback Triggers

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error Rate | > 1% for 5 minutes | Auto-rollback |
| Latency P99 | > 5 seconds | Alert + manual review |
| Database Errors | Any connection refused | Auto-rollback |
| Zod Validation Errors | > 100/minute | Auto-rollback |

### 5.4 Rollback Steps

```bash
# 1. Disable feature flag (immediate)
kubectl set env deployment/taskman-api FF_REAL_PROJECTS=false

# 2. Verify mock data endpoint responding
curl -X GET https://api.taskman.local/api/projects | jq '.projects[0].id'
# Should return: "P-CTX-001" (mock data)

# 3. If database migration was applied, revert
alembic downgrade -1

# 4. Monitor error rates
watch -n 5 'curl -s https://api.taskman.local/health | jq'
```

---

## 6. Summary Matrix

| Risk ID | Risk | Probability | Impact | Mitigation | Test Coverage |
|---------|------|-------------|--------|------------|---------------|
| MCP-001 | Datetime serialization | High | High | `format_datetime_for_mcp()` | Unit + Integration |
| MCP-002 | Schema drift | High | Medium | Explicit mapping layer | Contract tests |
| SQL-003 | N+1 queries | High | Medium | `selectinload()` pattern | Query analysis |
| SQL-004 | Pool exhaustion | Medium | High | Pool config + monitoring | Load tests |
| DBO-001 | Cascade delete | Medium | Critical | Block if children exist | Integration tests |
| DBO-002 | FK violations | High | Medium | Pre-validation | Integration tests |
| FPI-002 | Response validation | High | Medium | Use dict, explicit serialize | Unit tests |
| DBO-003 | Concurrent updates | Medium | Medium | Optimistic locking | Integration tests |

---

## Appendix A: Quick Reference Code Patterns

### A.1 Safe Route Template

```python
@router.post("/", status_code=201)
async def create_project(
    project: ProjectCreate,
    db: Annotated[AsyncSession, Depends(get_db_session)]
) -> dict:
    """Create project with all safety patterns applied"""
    correlation_id = f"create-project-{uuid4().hex[:8]}"
    
    try:
        # Create entity
        db_project = Project(
            id=generate_project_id(),
            **project.model_dump()
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        
        # Log success
        ulog("create_project_success", target=db_project.id, correlation_id=correlation_id)
        
        return serialize_project(db_project)
        
    except IntegrityError as e:
        await db.rollback()
        ulog("create_project_integrity_error", error=str(e), correlation_id=correlation_id)
        raise HTTPException(status_code=409, detail="Project with this name already exists")
    except Exception as e:
        await db.rollback()
        ulog("create_project_error", error=str(e), correlation_id=correlation_id)
        raise HTTPException(status_code=500, detail="Failed to create project")
```

### A.2 Serialization Utilities

```python
# python/api/utils/serialization.py

from datetime import datetime, timezone
from uuid import UUID
from decimal import Decimal
from typing import Any

def format_datetime_for_mcp(dt: datetime | None) -> str | None:
    """Format datetime to Zod isoDateTime compatible string"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def serialize_value(value: Any) -> Any:
    """Convert Python types to JSON-safe values"""
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return format_datetime_for_mcp(value)
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        return [serialize_value(v) for v in value]
    return value
```

---

**Document Control**
- Version: 1.0
- Approved by: Risk Pattern Analyst Agent
- Next Review: After implementation complete
