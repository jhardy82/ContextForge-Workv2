# TaskMan-v2 Backend API

FastAPI-based REST API server for TaskMan-v2 with PostgreSQL backend.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run development server (port 3001)
uvicorn main:app --reload --port 3001

# Or use Docker
docker-compose -f docker-compose.taskman-v2.yml up -d
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List all tasks |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks/{id}` | Get task by ID |
| PUT | `/api/v1/tasks/{id}` | Update task |
| DELETE | `/api/v1/tasks/{id}` | Delete task |
| GET | `/api/v1/projects` | List projects |
| GET | `/api/v1/sprints` | List sprints |
| GET | `/api/v1/health` | Health check |

## Project Structure

```
backend-api/
├── main.py              # FastAPI application entry
├── routers/             # API route handlers
│   ├── tasks.py         # Task CRUD endpoints
│   ├── projects.py      # Project endpoints
│   ├── sprints.py       # Sprint endpoints
│   └── action_lists.py  # Action list endpoints
├── schemas/             # Centralized Pydantic schemas
│   ├── __init__.py      # All exports
│   ├── enums.py         # TaskStatus, TaskPriority, etc.
│   ├── base.py          # Reusable mixins
│   ├── task.py          # TaskCreate, TaskResponse, etc.
│   ├── project.py       # Project schemas
│   ├── sprint.py        # Sprint schemas
│   └── action_list.py   # ActionList schemas
├── repositories/        # Data access layer
├── dependencies.py      # FastAPI dependencies
└── alembic/             # Database migrations
```

## Schemas Package

Centralized Pydantic v2 schemas aligned with database (40+ fields per entity):

**Enums** (`schemas/enums.py`):
- `TaskStatus`: new, ready, in_progress, blocked, review, done, dropped
- `TaskPriority`: p0, p1, p2, p3
- `ProjectStatus`: planning, active, on_hold, completed, cancelled
- `SprintStatus`: planning, active, completed, cancelled

**Base Mixins** (`schemas/base.py`):
- `TimestampMixin`: created_at, updated_at
- `ObservabilityMixin`: dashboards, alerts, logs, SLOs
- `OwnershipMixin`: owner, assignees, sponsors

## Testing

The backend includes a comprehensive test suite with 291 tests across multiple categories:

### Test Categories

| Category | Count | Location | Purpose |
|----------|-------|----------|---------|
| Unit | 150+ | `tests/unit/` | Component isolation tests |
| Integration | 15+ | `tests/integration/` | Service integration |
| E2E | 11 | `tests/e2e/` | Critical workflow validation |
| Regression | 12 | `tests/regression/` | API contract bug prevention |
| Performance | 10 | `tests/performance/` | Response time benchmarks |

### Running Tests

**VS Code Tasks (Recommended)**:

```bash
# Quick, reliable testing (default)
Ctrl+Shift+P → Tasks: Run Task → "Python: Pytest (direct)"

# With observability/debugging (requires profile guard)
Ctrl+Shift+P → Tasks: Run Task → "Python: Pytest (with-logging)"
```

**Command Line**:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/taskman_api --cov-report=html

# Run by category
pytest tests/unit/ -v
pytest tests/e2e/ -v
pytest tests/regression/ -v
pytest tests/performance/ -v

# Run specific test file
pytest tests/unit/routers/test_action_lists_router.py -v
```

**Troubleshooting**: If VS Code tasks fail with profile interference, see [docs/quick-reference/vscode-task-profile-fix.md](../../docs/quick-reference/vscode-task-profile-fix.md)

### CI/CD

Tests run automatically via GitHub Actions on push/PR:
- **Workflow**: `.github/workflows/taskman-backend-tests.yml`
- **Coverage**: Reported to Codecov
- **Quality**: Ruff lint + MyPy type check + Bandit security scan

## Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENVIRONMENT` | development | Environment mode |
| `APP_DATABASE__HOST` | localhost | PostgreSQL host |
| `APP_DATABASE__PORT` | 5432 | PostgreSQL port |
| `APP_DATABASE__DATABASE` | taskman | Database name |

See `.env.example` for complete configuration.
