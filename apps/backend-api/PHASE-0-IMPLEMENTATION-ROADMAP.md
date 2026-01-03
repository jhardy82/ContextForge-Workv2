# Phase 0: Backend API Implementation - Complete Roadmap

**Generated**: 2025-12-25
**Estimated Duration**: 40-60 hours
**Dependencies**: ✅ Configuration Complete (Phases 1-3)
**Status**: 🔄 Ready to Begin

---

## 📋 Executive Summary

Implement a production-ready FastAPI backend at `backend-api/` that provides 22 REST endpoints for the TypeScript MCP server. This is the **critical blocker** for 18 of 22 subsequent tasks in the TaskMan-v2 project.

**Key Achievement**: Transform the placeholder `backend-api/` directory into a fully functional REST API with 100% test coverage, type safety, and production-grade error handling.

---

## 🎯 Success Criteria

1. ✅ **22 REST Endpoints** implementing full CRUD for Tasks, Projects, Sprints, ActionLists
2. ✅ **PostgreSQL Integration** with SQLAlchemy 2.0+ async patterns
3. ✅ **Repository Pattern** with Result monad for error handling
4. ✅ **RFC 9457 Problem Details** for standardized error responses
5. ✅ **Structured Logging** (JSONL format) with correlation IDs
6. ✅ **100% Type Safety** with MyPy strict mode
7. ✅ **≥70% Test Coverage** (unit + integration tests)
8. ✅ **Port 3000** (matching TypeScript MCP configuration)

---

## 🔍 Research Summary

### Existing Resources Analyzed

1. **`RESEARCH-FINDINGS.md`** (698 lines)
   - Complete TypeScript MCP tool inventory (40+ tools)
   - Data model documentation (Task: 70+ fields)
   - API endpoint mapping (TypeScript → FastAPI)
   - Integration requirements

2. **`IMPLEMENTATION_QUICK_REFERENCE.md`** (370 lines)
   - Configuration module (✅ 100% complete)
   - Environment variables documented
   - Test patterns established

3. **`DATABASE-MODEL-EXPANSION-SUMMARY.md`** (549 lines)
   - 8 entity types with full schemas
   - ContextForge integration requirements
   - Relationship mappings

4. **TypeScript MCP Client** (`backend/client.ts`, 1417 lines)
   - API envelope pattern: `{ success: boolean, data?: T, error?: string }`
   - Retry logic: Exponential backoff (1s, 2s, 4s)
   - Headers: `x-request-id`, `x-correlation-id`, `x-concurrency-token`
   - Timeout: 30 seconds default

### External Research Completed

#### FastAPI Best Practices (2025)
**Sources**:
- [FastAPI with Async SQLAlchemy](https://testdriven.io/blog/fastapi-sqlmodel/)
- [FastAPI Best Practices Repository](https://github.com/zhanymkanov/fastapi-best-practices)
- [FastAPI Database Patterns](https://www.compilenrun.com/docs/framework/fastapi/fastapi-database/fastapi-database-patterns/)
- [Async Database Sessions in FastAPI](https://dev.to/akarshan/asynchronous-database-sessions-in-fastapi-with-sqlalchemy-1o7e)

**Key Patterns**:
- AsyncSession with `create_async_engine`
- Repository pattern for data access layer
- Dependency injection via FastAPI `Depends()`
- Structured project layout (api/services/db/schemas)

#### Result Monad Pattern
**Sources**:
- [Mastering Monad Design Patterns in Python](https://dev.to/hamzzak/mastering-monad-design-patterns-simplify-your-python-code-and-boost-efficiency-kal)
- [monadic-error PyPI Package](https://pypi.org/project/monadic-error/)
- [Python Functors and Monads Guide](https://arjancodes.com/blog/python-functors-and-monads/)

**Implementation**: Use `monadic-error` library for `Result[T, E]` pattern in service layer.

#### RFC 9457 Problem Details
**Sources**:
- [RFC 9457 Official Specification](https://www.rfc-editor.org/rfc/rfc9457.html)
- [Problem Details (RFC 9457): Doing API Errors Well](https://swagger.io/blog/problem-details-rfc9457-doing-api-errors-well/)
- [Understanding RFC 9457](https://medium.com/@mhd.umair/understanding-rfc-9457-problem-details-for-http-apis-6bdb675e685f)

**Required Fields**:
```python
{
    "type": "https://api.taskman-v2.local/problems/not-found",
    "title": "Task Not Found",
    "status": 404,
    "detail": "Task with ID 'task-123' does not exist",
    "instance": "/api/v1/tasks/task-123"
}
```

---

## 🏗️ Architecture Design

### Directory Structure

```
TaskMan-v2/backend-api/
├── src/
│   └── taskman_api/
│       ├── __init__.py
│       ├── main.py                    # FastAPI app + startup/shutdown
│       │
│       ├── config.py                  # ✅ COMPLETE (Phase 1)
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── enums.py               # TaskStatus, WorkType, Priority enums
│       │   ├── errors.py              # AppError base + specific errors
│       │   └── result.py              # Result[T, E] monad wrapper
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   ├── session.py             # AsyncSession factory
│       │   ├── base.py                # SQLAlchemy declarative base
│       │   └── models/
│       │       ├── __init__.py
│       │       ├── task.py            # Task model (70+ fields)
│       │       ├── project.py         # Project model (~40 fields)
│       │       ├── sprint.py          # Sprint model (~30 fields)
│       │       ├── action_list.py     # ActionList model (~18 fields)
│       │       ├── meta_task.py       # MetaTask model (~35 fields)
│       │       ├── comment.py         # Comment model (~20 fields)
│       │       ├── kb_article.py      # KBArticle model (~30 fields)
│       │       └── config_item.py     # ConfigItem model (~25 fields)
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── task.py                # TaskCreate, TaskUpdate, TaskResponse
│       │   ├── project.py             # Project schemas
│       │   ├── sprint.py              # Sprint schemas
│       │   └── action_list.py         # ActionList schemas
│       │
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── base.py                # BaseRepository[T] with CRUD
│       │   ├── task.py                # TaskRepository (bulk ops, search)
│       │   ├── project.py             # ProjectRepository
│       │   ├── sprint.py              # SprintRepository
│       │   └── action_list.py         # ActionListRepository
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── task_service.py        # Business logic + Result monad
│       │   ├── project_service.py     # Project business logic
│       │   ├── sprint_service.py      # Sprint business logic
│       │   └── action_list_service.py # ActionList business logic
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py                # Dependency injection (get_db, etc.)
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py          # APIRouter aggregation
│       │       ├── tasks.py           # 10 task endpoints
│       │       ├── projects.py        # 6 project endpoints
│       │       ├── sprints.py         # 5 sprint endpoints
│       │       └── action_lists.py    # 10 action list endpoints
│       │
│       └── infrastructure/
│           ├── __init__.py
│           ├── logging.py             # Structured logging (JSONL)
│           ├── middleware.py          # Correlation ID, error handling
│           └── health.py              # Health check endpoints
│
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py     # Complete schema migration
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # ✅ COMPLETE (Phase 1)
│   │
│   ├── unit/
│   │   ├── test_config.py             # ✅ COMPLETE (39 tests)
│   │   ├── test_fixtures.py           # ✅ COMPLETE (14 tests)
│   │   ├── test_errors.py             # Error handling tests
│   │   ├── test_result_monad.py       # Result pattern tests
│   │   ├── test_repositories.py       # Repository layer tests
│   │   └── test_services.py           # Service layer tests
│   │
│   └── integration/
│       ├── test_task_api.py           # Task endpoints E2E
│       ├── test_project_api.py        # Project endpoints E2E
│       ├── test_sprint_api.py         # Sprint endpoints E2E
│       └── test_action_list_api.py    # ActionList endpoints E2E
│
├── pyproject.toml                     # ✅ COMPLETE (221 lines)
├── alembic.ini
├── .env.example                       # ✅ COMPLETE (Phase 1)
├── .env.test                          # ✅ COMPLETE (Phase 1)
├── .env.production.example            # ✅ COMPLETE (Phase 1)
└── README.md                          # ✅ COMPLETE (Phase 1)
```

**Files to Create**: 40 files
**Lines of Code Estimate**: ~8,000 lines (code + tests)

---

## 📝 Implementation Phases

### Phase 0.1: Foundation (8-10 hours)

**Goal**: Establish core infrastructure and database models.

#### Tasks:
1. **Create Core Enums** (`core/enums.py`, 2h)
   - TaskStatus (7 values)
   - WorkType (6 values)
   - TaskPriority, Severity, RiskLevel (4 values each)
   - ProjectStatus, SprintStatus, ActionListStatus
   - GeometryShape, ShapeStage, ValidationState, Health

2. **Create Error System** (`core/errors.py`, 2h)
   - `AppError` base class with error codes
   - `NotFoundError`, `ConflictError`, `ValidationError`
   - RFC 9457 Problem Details conversion
   - Error code registry

3. **Create Result Monad** (`core/result.py`, 2h)
   - `Result[T, E]` type with Ok/Err states
   - Monadic operations (map, bind, match)
   - Integration with service layer

4. **Create SQLAlchemy Models** (`db/models/*.py`, 4-6h)
   - Task model (70+ fields)
   - Project model (~40 fields)
   - Sprint model (~30 fields)
   - ActionList model (~18 fields)
   - Relationships and indexes

**Deliverables**:
- 4 core modules operational
- Type checking passes (mypy --strict)
- Basic unit tests (20-30 tests)

---

### Phase 0.2: Database Layer (8-10 hours)

**Goal**: Implement repository pattern with async SQLAlchemy.

#### Tasks:
1. **Create Database Session** (`db/session.py`, 2h)
   - AsyncSession factory with connection pooling
   - Transaction management
   - Session lifecycle hooks

2. **Create Base Repository** (`repositories/base.py`, 3h)
   - Generic `BaseRepository[T]` with CRUD operations
   - `create()`, `read()`, `update()`, `delete()`
   - `list()` with filtering and pagination
   - Return `Result[T, AppError]` types

3. **Create Task Repository** (`repositories/task.py`, 3h)
   - Bulk operations: `bulk_update()`, `bulk_assign_sprint()`
   - Full-text search: `search()`
   - Complex filters (status, work_type, priority, project_id, sprint_id)

4. **Create Other Repositories** (`repositories/*.py`, 2-4h)
   - ProjectRepository with metrics calculation
   - SprintRepository with capacity tracking
   - ActionListRepository with item management

**Deliverables**:
- 4 repository classes
- 40-50 repository tests
- Database connection verified

---

### Phase 0.3: Service Layer (6-8 hours)

**Goal**: Implement business logic with Result monad pattern.

#### Tasks:
1. **Create Task Service** (`services/task_service.py`, 3h)
   - CRUD operations returning `Result[TaskResponse, AppError]`
   - Status transitions with validation
   - Assignment logic
   - Bulk operations

2. **Create Other Services** (`services/*.py`, 3-5h)
   - ProjectService with metrics aggregation
   - SprintService with capacity management
   - ActionListService with item reordering

**Deliverables**:
- 4 service classes
- 30-40 service tests
- Business logic validated

---

### Phase 0.4: API Endpoints (10-12 hours)

**Goal**: Implement 22 REST endpoints with FastAPI.

#### Tasks:
1. **Create Dependency Injection** (`api/deps.py`, 1h)
   - `get_db()` - Database session provider
   - `get_current_user()` - Placeholder (JWT integration Phase 4)
   - `get_correlation_id()` - Request tracing

2. **Create Task Endpoints** (`api/v1/tasks.py`, 4h)
   ```python
   POST   /api/v1/tasks                    # task_create
   GET    /api/v1/tasks/{task_id}          # task_read
   PATCH  /api/v1/tasks/{task_id}          # task_update
   PATCH  /api/v1/tasks/{task_id}/status   # task_set_status
   PATCH  /api/v1/tasks/{task_id}/assign   # task_assign
   DELETE /api/v1/tasks/{task_id}          # task_delete
   GET    /api/v1/tasks                    # task_list
   PATCH  /api/v1/tasks/bulk               # task_bulk_update
   POST   /api/v1/tasks/bulk/sprint        # task_bulk_assign_sprint
   POST   /api/v1/tasks/search             # task_search
   ```

3. **Create Project Endpoints** (`api/v1/projects.py`, 2h)
   ```python
   POST   /api/v1/projects                 # project_create
   GET    /api/v1/projects/{project_id}    # project_read
   PATCH  /api/v1/projects/{project_id}    # project_update
   DELETE /api/v1/projects/{project_id}    # project_delete
   GET    /api/v1/projects                 # project_list
   GET    /api/v1/projects/{project_id}/metrics  # project_get_metrics
   ```

4. **Create Sprint Endpoints** (`api/v1/sprints.py`, 2h)
   ```python
   POST   /api/v1/sprints                  # sprint_create
   GET    /api/v1/sprints/{sprint_id}      # sprint_read
   PATCH  /api/v1/sprints/{sprint_id}      # sprint_update
   DELETE /api/v1/sprints/{sprint_id}      # sprint_delete
   GET    /api/v1/sprints                  # sprint_list
   ```

5. **Create ActionList Endpoints** (`api/v1/action_lists.py`, 2h)
   ```python
   POST   /api/v1/action-lists             # action_list_create
   GET    /api/v1/action-lists/{list_id}   # action_list_read
   PATCH  /api/v1/action-lists/{list_id}   # action_list_update
   DELETE /api/v1/action-lists/{list_id}   # action_list_delete
   GET    /api/v1/action-lists             # action_list_list
   ```

6. **Create Main App** (`main.py`, 1h)
   - FastAPI app initialization
   - Router registration
   - Middleware setup (CORS, logging, error handling)
   - Startup/shutdown events

**Deliverables**:
- 22 REST endpoints operational
- API documentation via /docs
- Swagger UI accessible

---

### Phase 0.5: Infrastructure (4-6 hours)

**Goal**: Implement logging, error handling, and health checks.

#### Tasks:
1. **Create Structured Logging** (`infrastructure/logging.py`, 2h)
   - JSONL format with correlation IDs
   - Request/response logging middleware
   - Error logging with stack traces
   - Integration with structlog

2. **Create Error Middleware** (`infrastructure/middleware.py`, 2h)
   - RFC 9457 Problem Details responses
   - Exception → AppError mapping
   - Validation error formatting
   - 500 error handling with logging

3. **Create Health Checks** (`infrastructure/health.py`, 1h)
   ```python
   GET /health/live     # Liveness probe
   GET /health/ready    # Readiness probe (DB check)
   GET /health/startup  # Startup probe
   ```

**Deliverables**:
- Structured logging operational
- Error responses standardized
- Health checks functional

---

### Phase 0.6: Database Migrations (2-3 hours)

**Goal**: Create Alembic migrations for complete schema.

#### Tasks:
1. **Configure Alembic** (`alembic/env.py`, 1h)
   - Async engine support
   - Model import registration
   - Configuration from Settings

2. **Create Initial Migration** (`alembic/versions/001_initial_schema.py`, 1-2h)
   - All 8 entity tables (tasks, projects, sprints, action_lists, meta_tasks, comments, kb_articles, config_items)
   - Indexes for performance
   - Foreign key constraints
   - Check constraints for enums

**Deliverables**:
- Alembic configured
- Initial migration tested
- Schema deployed to PostgreSQL

---

### Phase 0.7: Testing & Validation (8-10 hours)

**Goal**: Achieve ≥70% test coverage with comprehensive tests.

#### Tasks:
1. **Unit Tests** (`tests/unit/*.py`, 4-5h)
   - Error system tests
   - Result monad tests
   - Repository tests (with in-memory DB)
   - Service tests (with mocked repositories)

2. **Integration Tests** (`tests/integration/*.py`, 4-5h)
   - Task API E2E tests (all 10 endpoints)
   - Project API E2E tests (all 6 endpoints)
   - Sprint API E2E tests (all 5 endpoints)
   - ActionList API E2E tests (all 5 endpoints)

**Deliverables**:
- ≥70% code coverage
- All tests passing
- Coverage report generated

---

### Phase 0.8: Documentation & Polish (2-3 hours)

**Goal**: Complete documentation and final cleanup.

#### Tasks:
1. **Update README** (`README.md`, 1h)
   - Quick start guide
   - API endpoint list
   - Configuration reference
   - Development workflow

2. **Create API Documentation** (1h)
   - OpenAPI/Swagger annotations
   - Request/response examples
   - Error response documentation

3. **Final Cleanup** (1h)
   - Remove placeholder code
   - Update .env.example
   - Verify all tests pass
   - Run linting (ruff, mypy, bandit)

**Deliverables**:
- Comprehensive README
- Swagger UI documentation
- Clean codebase

---

## 🔢 Effort Breakdown

| Phase | Tasks | Hours | Status |
|-------|-------|-------|--------|
| **0.1: Foundation** | Core infrastructure, models | 8-10h | Pending |
| **0.2: Database Layer** | Repository pattern, async SQLAlchemy | 8-10h | Pending |
| **0.3: Service Layer** | Business logic, Result monad | 6-8h | Pending |
| **0.4: API Endpoints** | 22 REST endpoints | 10-12h | Pending |
| **0.5: Infrastructure** | Logging, errors, health | 4-6h | Pending |
| **0.6: Migrations** | Alembic setup, initial schema | 2-3h | Pending |
| **0.7: Testing** | Unit + integration tests | 8-10h | Pending |
| **0.8: Documentation** | README, API docs, cleanup | 2-3h | Pending |

**Total Estimated Effort**: 48-62 hours
**Critical Path Duration**: ~40 hours (with some parallelization)

---

## 📚 Technical Stack

### Core Dependencies
```python
fastapi = ">=0.115,<0.116"       # Web framework
uvicorn = ">=0.32,<0.33"          # ASGI server
pydantic = ">=2.9,<3.0"           # Data validation
pydantic-settings = ">=2.5,<3.0"  # ✅ COMPLETE
sqlalchemy = ">=2.0,<3.0"         # ORM with async support
asyncpg = ">=0.30,<1.0"           # PostgreSQL async driver
alembic = ">=1.13,<2.0"           # Migrations
```

### Additional Libraries
```python
monadic-error = "latest"          # Result monad pattern
structlog = ">=24.4,<25.0"        # Structured logging
httpx = ">=0.27,<0.28"            # HTTP client (testing)
python-jose = ">=3.3,<4.0"        # JWT (Phase 4)
```

### Dev Dependencies (✅ Already Configured)
```python
pytest = ">=8.3,<9.0"
pytest-asyncio = ">=0.24,<1.0"
pytest-cov = ">=5.0,<6.0"
ruff = ">=0.6,<0.7"               # Linting
mypy = ">=1.11,<1.12"             # Type checking
bandit = ">=1.7,<2.0"             # Security
```

---

## 🎯 Quality Gates

### Code Quality
- ✅ MyPy strict mode passing (no type: ignore comments)
- ✅ Ruff linting passing (zero errors)
- ✅ Bandit security scan passing (zero high/critical issues)
- ✅ Line length ≤100 characters
- ✅ Import sorting (isort via ruff)

### Testing
- ✅ ≥70% overall coverage (target: 80%)
- ✅ 100% coverage for error handling
- ✅ All pytest markers correctly applied
- ✅ Async tests using pytest-asyncio
- ✅ Integration tests use test database

### Documentation
- ✅ All public functions have docstrings
- ✅ All endpoints have OpenAPI annotations
- ✅ README has complete setup instructions
- ✅ .env.example is up-to-date

---

## 🔗 Integration Points

### TypeScript MCP Client Expectations
```typescript
// Expected API response envelope
interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Expected headers
"Content-Type": "application/json"
"x-request-id": string          // Correlation ID
"x-correlation-id": string      // Request tracing
"x-concurrency-token": string   // Optimistic locking (optional)
```

### Database Configuration
```bash
# PostgreSQL connection (from Phase 1 config)
DATABASE_HOST=172.25.14.122
DATABASE_PORT=5432
DATABASE_USER=taskman
DATABASE_PASSWORD=<secure>
DATABASE_DATABASE=taskman_v2
```

### Port Standardization
```bash
# Backend API runs on port 3000 (CORRECTED in Phase 2)
PORT=3000
# TypeScript MCP connects to http://localhost:3000/api/v1
TASK_MANAGER_API_ENDPOINT=http://localhost:3000/api/v1
```

---

## 🚧 Known Challenges

### 1. Data Model Complexity
**Challenge**: Task model has 70+ fields with rich ContextForge integration.

**Mitigation**:
- Use SQLAlchemy column grouping
- Pydantic field categorization
- Optional fields with sensible defaults
- Comprehensive validation

### 2. Async SQLAlchemy Patterns
**Challenge**: Async session management requires careful lifecycle handling.

**Mitigation**:
- Use `async with` context managers
- Dependency injection via FastAPI
- Test with pytest-asyncio
- Follow 2025 best practices from research

### 3. Result Monad Integration
**Challenge**: Monadic error handling is unfamiliar pattern.

**Mitigation**:
- Use `monadic-error` library
- Comprehensive examples in tests
- Clear documentation
- Pattern matching with Python 3.11+

### 4. RFC 9457 Problem Details
**Challenge**: Standardized error format requires middleware.

**Mitigation**:
- Custom exception handler
- AppError → Problem Details mapping
- Comprehensive error codes
- Client-friendly messages

---

## 📋 Next Steps After Phase 0

**Immediate**:
1. **Phase 4: Integration Testing** (3-4h)
   - MCP server → Backend API end-to-end
   - Validate API envelope pattern
   - Test correlation IDs
   - Verify error handling

**Unblocked Tasks** (18 total):
- TASK-001: Express-Rate-Limit (3-4h)
- TASK-002: Helmet Middleware (2-3h)
- TASK-003: Migrate 22 Endpoints to AppError (6-8h)
- TASK-004: Compression Middleware (2-3h)
- TASK-005: Bulk-Update Endpoint (4-6h)
- TASK-006: Search Endpoint (4-6h)
- TASK-007: TypeScript MCP Validation (3-4h)
- ... and 11 more tasks

---

## 📖 References

### Research Documents
- `RESEARCH-FINDINGS.md` - Complete MCP tool inventory
- `IMPLEMENTATION_QUICK_REFERENCE.md` - Configuration reference
- `DATABASE-MODEL-EXPANSION-SUMMARY.md` - Schema documentation
- `CONFIGURATION-PHASE-1-COMPLETE.md` - Python config (✅ complete)
- `CONFIGURATION-PHASE-2-COMPLETE.md` - TypeScript config (✅ complete)
- `CONFIGURATION-PHASE-3-COMPLETE.md` - Environment files (✅ complete)

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic Settings V2](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [RFC 9457 Specification](https://www.rfc-editor.org/rfc/rfc9457.html)
- [Python Monadic Error](https://pypi.org/project/monadic-error/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

## ✅ Pre-Implementation Checklist

Before starting Phase 0.1:

- [x] Configuration module complete (Phase 1)
- [x] TypeScript MCP configuration complete (Phase 2)
- [x] Environment files created (Phase 3)
- [x] Research completed (RESEARCH-FINDINGS.md)
- [x] Database schema documented
- [x] API endpoints mapped
- [x] pyproject.toml configured
- [x] .env.example files created
- [x] PostgreSQL connection verified
- [ ] User approval to begin implementation

---

**"From Research to Reality: 40-60 hours to unlock 18 blocked tasks."**
