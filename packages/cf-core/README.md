# cf_core - ContextForge Core Domain Library

**Version**: 0.1.0
**Status**: Active Development - Canonical Implementation
**Architecture**: Domain-Driven Design (DDD) with Repository Pattern and Result Monad

---

## Quick Start

```python
from cf_core.domain.sprint_entity import SprintEntity
from cf_core.repositories.sprint_repository import SQLiteSprintRepository
from cf_core.shared.result import Result

# Create repository
repo = SQLiteSprintRepository("db/sprints.db")

# Create new sprint entity
sprint = SprintEntity.create(
    sprint_id="SPRINT-001",
    title="Q1 2025 Sprint",
    status="planned",
    goal="Complete P0 critical tasks"
)

# Save with Result monad error handling
result = repo.save(sprint)
if result.is_success:
    print(f"Sprint saved: {result.value}")
else:
    print(f"Error: {result.error}")
```

---

## Purpose

`cf_core` is the canonical domain layer for ContextForge task management, implementing clean architecture principles with:

- **Domain-Driven Design** patterns for rich business logic
- **Repository Pattern** for persistence abstraction
- **Result Monad** for functional error handling
- **Clean Architecture** for maintainability and testability

This package provides the core domain models, entities, repositories, and shared utilities used across ContextForge projects.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Structure](#directory-structure)
3. [Core Concepts](#core-concepts)
4. [Repository Pattern](#repository-pattern)
5. [Result Monad Error Handling](#result-monad-error-handling)
6. [Domain Entities](#domain-entities)
7. [Quick Reference Examples](#quick-reference-examples)
8. [Testing Guide](#testing-guide)
9. [Integration Points](#integration-points)
10. [Migration Status](#migration-status)
11. [See Also](#see-also)

---

## Architecture Overview

### Domain-Driven Design (DDD)

`cf_core` follows tactical DDD patterns:

```
┌─────────────────────────────────────────────┐
│           Application Layer                 │
│        (TaskMan-v2, QSE, CLI)              │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         cf_core Domain Layer                │
│                                              │
│  ┌────────────┐  ┌────────────┐            │
│  │  Entities  │  │ Value      │            │
│  │            │  │ Objects    │            │
│  └────────────┘  └────────────┘            │
│                                              │
│  ┌────────────┐  ┌────────────┐            │
│  │Repositories│  │  Services  │            │
│  └────────────┘  └────────────┘            │
│                                              │
│  ┌────────────────────────────┐            │
│  │  Shared (Result, Utils)    │            │
│  └────────────────────────────┘            │
└──────────────┬──────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│      Infrastructure Layer                    │
│   (SQLite, PostgreSQL, APIs)                │
└──────────────────────────────────────────────┘
```

### Layers

1. **Domain Layer** (`domain/`): Entities with business logic (SprintEntity, TaskEntity)
2. **Repository Layer** (`repositories/`): Persistence abstraction (IRepository, SQLite implementations)
3. **Model Layer** (`models/`): Data structures (Pydantic models)
4. **Shared Layer** (`shared/`): Cross-cutting concerns (Result monad, exceptions)
5. **Service Layer** (`services/`): Application services and orchestration
6. **Infrastructure Layer** (`cli/`, `health/`, `logging/`, `migrate/`): Supporting utilities

---

## Directory Structure

```
cf_core/
├── __init__.py              # Package metadata
├── README.md                # This file
│
├── domain/                  # Domain entities (business logic)
│   ├── __init__.py
│   └── sprint_entity.py     # SprintEntity with state management
│
├── repositories/            # Repository pattern implementations
│   ├── __init__.py
│   └── sprint_repository.py # ISprintRepository + SQLiteSprintRepository
│
├── models/                  # Pydantic data models
│   ├── __init__.py
│   ├── sprint.py            # Sprint model
│   ├── task.py              # Task model
│   ├── project.py           # Project model
│   └── context.py           # Context model
│
├── shared/                  # Shared utilities
│   ├── __init__.py
│   ├── result.py            # Result monad for error handling
│   └── exceptions.py        # Custom exceptions
│
├── services/                # Application services
│   └── __init__.py
│
├── cli/                     # CLI with Rich output + JSONL logging
│   ├── main.py              # Typer CLI entry point (Plugin Loader)
│   └── output.py            # Dual output adapter (Rich + JSONL)
├── health/                  # Health check utilities
├── logging/                 # Logging configuration
├── migrate/                 # Database migration tools
├── utils/                   # General utilities
└── fallback/                # Fallback mechanisms
```

---

## Core Concepts

### 1. Entities

**What**: Objects with unique identity that encapsulate business logic

**Example**: `SprintEntity`

```python
from cf_core.domain.sprint_entity import SprintEntity

# Create new sprint
sprint = SprintEntity.create(
    sprint_id="SPRINT-Q1-2025",
    title="Q1 2025 Feature Sprint",
    status="planned",
    goal="Implement authentication and CI/CD"
)

# Domain methods for state transitions
sprint.start()              # Change status to "active"
sprint.complete()           # Change status to "completed"
sprint.can_start()          # Business rule validation
```

### 2. Value Objects

**What**: Immutable objects defined by their attributes, not identity

**Example**: Pydantic models in `models/`

```python
from cf_core.models.sprint import Sprint

# Value object - compared by values
sprint = Sprint(
    sprint_id="SPRINT-001",
    title="My Sprint",
    status="planned"
)
```

### 3. Aggregates

**What**: Cluster of domain objects treated as a single unit

**Example**: Sprint aggregate (Sprint + Tasks + Metrics)

```python
# Sprint is the aggregate root
sprint = SprintEntity.create(...)

# Access related entities through aggregate
sprint.add_task(task)
sprint.calculate_velocity()
```

### 4. Repositories

**What**: Abstraction for data persistence, provides collection-like interface

**Example**: `ISprintRepository`

```python
from cf_core.repositories.sprint_repository import ISprintRepository

# Abstract interface
class ISprintRepository(ABC):
    def save(self, entity: SprintEntity) -> Result[SprintEntity]: ...
    def get_by_id(self, sprint_id: str) -> Result[SprintEntity]: ...
    def find_all(self) -> Result[List[SprintEntity]]: ...
```

---

## Repository Pattern

### Why Repository Pattern?

**Benefits**:
- Decouples domain logic from persistence
- Enables testing with in-memory repositories
- Allows swapping data sources (SQLite → PostgreSQL)
- Provides clean, collection-like interface

### Interface Definition

```python
from abc import ABC, abstractmethod
from cf_core.shared.result import Result

class ISprintRepository(ABC):
    """Abstract repository interface"""

    @abstractmethod
    def save(self, entity: SprintEntity) -> Result[SprintEntity]:
        """Save or update entity"""
        pass

    @abstractmethod
    def get_by_id(self, sprint_id: str) -> Result[SprintEntity]:
        """Retrieve by ID"""
        pass

    @abstractmethod
    def find_by_status(self, status: str) -> Result[List[SprintEntity]]:
        """Query by status"""
        pass
```

### Concrete Implementation

```python
from cf_core.repositories.sprint_repository import SQLiteSprintRepository

# Create repository with SQLite backend
repo = SQLiteSprintRepository("db/sprints.db")

# Use repository
result = repo.save(sprint)
result = repo.get_by_id("SPRINT-001")
result = repo.find_by_status("active")
```

### Testing with Mock Repository

```python
class InMemorySprintRepository(ISprintRepository):
    """Test double for unit tests"""

    def __init__(self):
        self._sprints = {}

    def save(self, entity):
        self._sprints[entity.sprint_id] = entity
        return Result.success(entity)

    def get_by_id(self, sprint_id):
        if sprint_id in self._sprints:
            return Result.success(self._sprints[sprint_id])
        return Result.failure(f"Sprint {sprint_id} not found")
```

---

## Result Monad Error Handling

### Why Result Monad?

**Traditional Exception Handling**:
```python
# Hidden error paths, unclear what can fail
def get_sprint(sprint_id: str) -> Sprint:
    # Might raise NotFoundException
    # Might raise DatabaseError
    # Caller doesn't know without reading docs/source
    return sprint
```

**Result Monad Approach**:
```python
# Explicit error handling, type-safe
def get_sprint(sprint_id: str) -> Result[Sprint]:
    # Returns Result.success(sprint) or Result.failure(error)
    # Caller MUST check is_success/is_failure
    # All error paths are explicit
    return result
```

### Basic Usage

```python
from cf_core.shared.result import Result

# Create success result
result = Result.success(42)
if result.is_success:
    print(result.value)  # 42

# Create failure result
result = Result.failure("Not found")
if result.is_failure:
    print(result.error)  # "Not found"
```

### Real-World Example

```python
from cf_core.repositories.sprint_repository import SQLiteSprintRepository

repo = SQLiteSprintRepository("db/sprints.db")

# Get sprint - returns Result[SprintEntity]
result = repo.get_by_id("SPRINT-001")

# Pattern 1: Check success/failure
if result.is_success:
    sprint = result.value
    print(f"Found sprint: {sprint.title}")
else:
    print(f"Error: {result.error}")

# Pattern 2: Handle both cases
sprint = result.value if result.is_success else None
error_msg = result.error if result.is_failure else None

# Pattern 3: Raise exception if needed
if result.is_failure:
    raise RuntimeError(result.error)
sprint = result.value
```

### Chaining Operations

```python
# Get sprint, update it, save it
result = repo.get_by_id("SPRINT-001")
if result.is_success:
    sprint = result.value
    sprint.start()

    save_result = repo.save(sprint)
    if save_result.is_success:
        print("Sprint started and saved")
    else:
        print(f"Save failed: {save_result.error}")
else:
    print(f"Get failed: {result.error}")
```

---

## Domain Entities

### SprintEntity

**Purpose**: Encapsulates sprint business logic and state transitions

**Location**: `cf_core/domain/sprint_entity.py`

**Example**:

```python
from cf_core.domain.sprint_entity import SprintEntity
from datetime import datetime

# Factory method to create new sprint
sprint = SprintEntity.create(
    sprint_id="SPRINT-Q1-001",
    title="Authentication Sprint",
    status="planned",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 14),
    goal="Implement JWT auth and CI/CD",
    project_id="PROJECT-001"
)

# Domain methods
sprint.start()              # Transition to "active"
sprint.complete()           # Transition to "completed"
sprint.can_start()          # Validate if sprint can start

# Access underlying model
sprint_model = sprint.to_model()
```

### TaskEntity (Future)

**Status**: Planned (not yet implemented)

**Purpose**: Task management with status transitions, priority, and assignment

### ProjectEntity (Future)

**Status**: Planned (not yet implemented)

**Purpose**: Project aggregation of sprints and tasks

---

## Quick Reference Examples

### Example 1: Create and Save Sprint

```python
from cf_core.domain.sprint_entity import SprintEntity
from cf_core.repositories.sprint_repository import SQLiteSprintRepository

# Create repository
repo = SQLiteSprintRepository("db/sprints.db")

# Create sprint
sprint = SprintEntity.create(
    sprint_id="SPRINT-001",
    title="My Sprint",
    status="planned"
)

# Save
result = repo.save(sprint)
if result.is_success:
    print("Sprint created successfully!")
else:
    print(f"Failed to create sprint: {result.error}")
```

### Example 2: Retrieve and Update Sprint

```python
# Get sprint by ID
result = repo.get_by_id("SPRINT-001")

if result.is_success:
    sprint = result.value

    # Start the sprint
    sprint.start()

    # Save updated sprint
    save_result = repo.save(sprint)
    if save_result.is_success:
        print("Sprint started!")
```

### Example 3: Query Sprints by Status

```python
# Find all active sprints
result = repo.find_by_status("active")

if result.is_success:
    active_sprints = result.value
    print(f"Found {len(active_sprints)} active sprints")

    for sprint in active_sprints:
        print(f"  - {sprint.title}")
```

### Example 4: Get Current Sprint

```python
# Get the currently active sprint
result = repo.get_current()

if result.is_success:
    current = result.value
    if current:
        print(f"Current sprint: {current.title}")
    else:
        print("No active sprint")
else:
    print(f"Error: {result.error}")
```

---

## Testing Guide

### Unit Testing Domain Entities

```python
# tests/cf_core/unit/domain/test_sprint_entity.py
import pytest
from cf_core.domain.sprint_entity import SprintEntity

def test_create_sprint():
    """Test sprint creation"""
    sprint = SprintEntity.create(
        sprint_id="TEST-001",
        title="Test Sprint",
        status="planned"
    )

    assert sprint.sprint_id == "TEST-001"
    assert sprint.title == "Test Sprint"
    assert sprint.status == "planned"

def test_sprint_start_transition():
    """Test sprint can transition to active"""
    sprint = SprintEntity.create(
        sprint_id="TEST-001",
        title="Test Sprint",
        status="planned"
    )

    sprint.start()
    assert sprint.status == "active"
```

### Unit Testing Repositories with Mocks

```python
# tests/cf_core/unit/repositories/test_sprint_repository.py
import pytest
from cf_core.domain.sprint_entity import SprintEntity
from tests.cf_core.mocks.in_memory_sprint_repository import InMemorySprintRepository

@pytest.fixture
def repo():
    """Provide in-memory repository for testing"""
    return InMemorySprintRepository()

def test_save_sprint(repo):
    """Test saving sprint"""
    sprint = SprintEntity.create(
        sprint_id="TEST-001",
        title="Test Sprint"
    )

    result = repo.save(sprint)

    assert result.is_success
    assert result.value.sprint_id == "TEST-001"

def test_get_nonexistent_sprint(repo):
    """Test getting sprint that doesn't exist"""
    result = repo.get_by_id("NONEXISTENT")

    assert result.is_failure
    assert "not found" in result.error.lower()
```

### Integration Testing with Real Database

```python
# tests/cf_core/integration/test_sprint_repository_sqlite.py
import pytest
import tempfile
from pathlib import Path
from cf_core.repositories.sprint_repository import SQLiteSprintRepository
from cf_core.domain.sprint_entity import SprintEntity

@pytest.fixture
def db_path():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        yield f.name
    Path(f.name).unlink(missing_ok=True)

def test_roundtrip_sprint(db_path):
    """Test save and retrieve sprint"""
    repo = SQLiteSprintRepository(db_path)

    # Create and save
    sprint = SprintEntity.create(
        sprint_id="INT-001",
        title="Integration Test Sprint"
    )
    save_result = repo.save(sprint)
    assert save_result.is_success

    # Retrieve
    get_result = repo.get_by_id("INT-001")
    assert get_result.is_success
    assert get_result.value.title == "Integration Test Sprint"
```

### Running Tests

```bash
# Run all cf_core tests
pytest tests/cf_core/

# Run unit tests only
pytest tests/cf_core/unit/

# Run with coverage
pytest tests/cf_core/ --cov=cf_core --cov-report=html

# Run specific test file
pytest tests/cf_core/unit/domain/test_sprint_entity.py

# Run with verbose output
pytest tests/cf_core/ -v
```

---

## Integration Points

### TaskMan-v2 Integration

**Location**: `TaskMan-v2/backend-api/`

**Usage**: TaskMan-v2 uses `cf_core` for domain models and repositories

```python
# In TaskMan-v2
from cf_core.models.task import Task
from cf_core.domain.sprint_entity import SprintEntity
from cf_core.repositories.sprint_repository import SQLiteSprintRepository

# FastAPI endpoint using cf_core
@router.get("/sprints/{sprint_id}")
async def get_sprint(sprint_id: str):
    repo = SQLiteSprintRepository(settings.DB_PATH)
    result = repo.get_by_id(sprint_id)

    if result.is_failure:
        raise HTTPException(status_code=404, detail=result.error)

    return result.value.to_model()
```

### QSE Framework Integration

**Location**: `.QSE/v2/`

**Usage**: QSE uses `cf_core` models for sprint and task tracking

```python
# In QSE
from cf_core.models.sprint import Sprint
from cf_core.models.task import Task

# QSE session uses cf_core for data models
session_data = {
    "sprint": Sprint(sprint_id="...", title="...", status="..."),
    "tasks": [Task(task_id="...", title="...", status="...")]
}
```

### CLI Integration

**Location**: `cf_core/cli/main.py` (canonical CLI), `output.py` (dual output adapter)

**Usage**: CLI provides human-readable Rich output + machine-readable JSONL logging

```bash
# Human-readable mode (default) - Rich tables and panels
cf task list (legacy)
cf taskman status (Plugin)
cf sprint show S-20251215233123
cf project list

# Machine mode - JSON to stdout for AI/automation
cf --machine task list
cf --machine sprint show S-001
```

**Output Features**:

| Command Type | Human Mode | Machine Mode |
|--------------|-----------|--------------|
| List (task/sprint/project) | Rich table with columns | JSON array |
| Get (single record) | Rich panel with labeled fields | JSON object |
| Create/Update/Delete | Success/error messages | JSON status |

**Session Logging**: All commands write to `logs/cli_session_<timestamp>.log` (JSONL format)

```python
# In cf_core/cli/main.py
from cf_core.cli.output import get_output

out = get_output()
out.table("Tasks", task_data, columns=["id", "title", "status"])
out.panel(content, title="Task: T-001", style="blue")
```

---

## Migration Status

### Current State: Canonical Implementation

**Location**: `cf_core/` (root level)

**Status**: **ACTIVE** - This is the canonical, production implementation

**Components**:
- Domain entities (SprintEntity)
- Repositories (ISprintRepository, SQLiteSprintRepository)
- Result monad (Result)
- Pydantic models (Sprint, Task, Project, Context)

### Legacy Locations (REMOVED)

**Previous Location**: `src/cf_core/` (REMOVED as of 2025-11-10)

**Status**: Removed per P0-002 remediation task

**Migration**: All references updated to use `cf_core/` directly

### Python Package Location

**Location**: `python/cf_core/` (LIMITED SCOPE)

**Status**: Special-purpose, contains only database config

**Files**:
- `__init__.py` (minimal)
- `database.py` (database configuration utilities)

**Note**: This is NOT the main cf_core implementation. Use `cf_core/` at root level.

### How to Use Correct Location

```python
# CORRECT - Use root-level cf_core
from cf_core.domain.sprint_entity import SprintEntity
from cf_core.repositories.sprint_repository import SQLiteSprintRepository
from cf_core.shared.result import Result

# INCORRECT - Do not use src/cf_core (removed)
# from src.cf_core.domain.sprint_entity import SprintEntity  # ERROR

# SPECIAL CASE - python/cf_core only for database config
from python.cf_core.database import get_database_url
```

---

## See Also

### Related Documentation

- [CF-CORE-MIGRATION-ANALYSIS.md](../projects/P-CFWORK-DOCUMENTATION/CF-CORE-MIGRATION-ANALYSIS.md) - Migration analysis and DDD patterns
- [TASKMAN-V2-ARCHITECTURE.md](../projects/P-CFWORK-DOCUMENTATION/TASKMAN-V2-ARCHITECTURE.md) - TaskMan-v2 architecture using cf_core
- [REMEDIATION-IMPLEMENTATION-PLAN.md](../projects/P-CFWORK-DOCUMENTATION/REMEDIATION-IMPLEMENTATION-PLAN.md) - Implementation roadmap

### External Resources

- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html) - Martin Fowler's introduction
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html) - Pattern description
- [Result Type](https://doc.rust-lang.org/std/result/) - Rust's Result<T, E> (inspiration)
- [Pydantic](https://docs.pydantic.dev/) - Data validation library used for models

### Code Examples

- `tests/cf_core/unit/` - Unit test examples
- `tests/cf_core/integration/` - Integration test examples
- `TaskMan-v2/backend-api/` - Real-world usage in FastAPI

---

## Contributing

### Adding New Domain Entities

1. **Create Pydantic model** in `models/`:
   ```python
   # cf_core/models/my_entity.py
   from pydantic import BaseModel

   class MyEntity(BaseModel):
       entity_id: str
       name: str
   ```

2. **Create domain entity** in `domain/`:
   ```python
   # cf_core/domain/my_entity.py
   from cf_core.models.my_entity import MyEntity

   class MyEntityEntity:
       def __init__(self, model: MyEntity):
           self._model = model

       @classmethod
       def create(cls, entity_id: str, name: str):
           return cls(MyEntity(entity_id=entity_id, name=name))
   ```

3. **Create repository interface and implementation** in `repositories/`:
   ```python
   # cf_core/repositories/my_entity_repository.py
   from abc import ABC, abstractmethod
   from cf_core.shared.result import Result

   class IMyEntityRepository(ABC):
       @abstractmethod
       def save(self, entity) -> Result: ...

       @abstractmethod
       def get_by_id(self, entity_id: str) -> Result: ...
   ```

4. **Write tests** in `tests/cf_core/unit/` and `tests/cf_core/integration/`

### Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Document all public methods with docstrings
- Use Result monad for error handling (no exceptions for expected errors)
- Write unit tests for all new functionality

---

## Version History

- **0.1.0** (Current) - Initial canonical implementation
  - SprintEntity with domain logic
  - SQLiteSprintRepository with Result monad
  - Result monad error handling
  - Pydantic models for data validation

---

## License

[Project License - Update as appropriate]

---

## Contact

For questions or issues related to `cf_core`:
- Create an issue in the repository
- Contact the ContextForge team
- See [PERSONA-TEAMS.md](../projects/P-CFWORK-DOCUMENTATION/PERSONA-TEAMS.md) for team structure

---

**Last Updated**: 2025-11-11
**Maintained By**: ContextForge Team (Team Delta - Architecture & Migration)
**Status**: Active Development
