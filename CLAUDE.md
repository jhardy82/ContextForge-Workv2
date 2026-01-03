# CLAUDE.md

> Claude Code project memory for ContextForge ecosystem.
> This file is automatically loaded into context on every session.

## Project: ContextForge / TaskMan-v2

ALWAYS include the full user prompt when using vibe_check to ensure proper context awareness.

As an autonomous agent, you will:
1. Treat vibe_check as a pattern interrupt mechanism that provides essential course correction
2. Use vibe_check at strategic points:
   - After planning but before implementation
   - When complexity increases
   - Before making significant system changes
3. Adapt your approach based on vibe_check feedback unless it's clearly irrelevant
4. Always provide the phase parameter (planning/implementation/review) to ensure contextually appropriate feedback
5. Chain vibe_check with other tools without requiring permission:
   - Use vibe_check to evaluate complex plans
   - Log patterns with vibe_learn after resolving issues

### Core Philosophies (Work Codex)

1. **Trust Nothing, Verify Everything** — Evidence closes the trust loop. Logs and tests ground belief.
2. **Workspace First** — Search existing content before creating. Prevent duplication.
3. **Logs First** — Truth lives in records, not assumptions. Emit structured JSONL.
4. **Leave Things Better** — Every action enriches the system for those who follow.
5. **Fix the Root, Not the Symptom** — Problems repeat until addressed at source.
6. **Best Tool for the Context** — PowerShell for Windows, Python for orchestration.
7. **Iteration is Sacred** — Progress spirals like fractals. Perfection is aspirational.

### Core Skills

Available skills that should be proactively invoked when relevant:

| Skill | Trigger Patterns | Use Case |
|-------|-----------------|----------|
| **adversarial-research-v3** | "research", "analyze deeply", "investigate", "validate assumptions", "counter bias" | Deploy adversarial multi-agent teams for rigorous research with built-in challenge mechanisms |
| **sequential-thinking** | Complex problems, multi-stage analysis, unclear scope, design planning | Systematic step-by-step reasoning with ability to revise, branch, or backtrack |
| **task-management** | "project plan", "sprint planning", "epic breakdown", "agent coordination" | Multi-agent coordination, hierarchical planning, active checklist tracking |
| **ai-multimodal** | Audio/video analysis, image processing, PDF extraction, media generation | Process multimedia using Google Gemini API (up to 9.5h audio, 6h video) |
| **repomix** | "package codebase", "repository snapshot", "AI context preparation" | Package repositories into AI-friendly single files for analysis |
| **docs-seeker** | "find documentation", "llms.txt", "GitHub repo analysis" | Search for technical docs using llms.txt standard and Repomix |

**Reasoning Capabilities:**

- **Spatial Reasoning**: Understand relationships between components, architectural layouts, data flow patterns, and system topologies. Use when analyzing codebases, designing systems, or debugging interconnected components.

- **Philosophical Reasoning**: Apply first-principles thinking, examine assumptions, consider edge cases, and evaluate trade-offs. Use for architectural decisions, ethical considerations, and complex problem decomposition.

- **Adversarial Reasoning**: Challenge your own conclusions, seek counter-evidence, identify blind spots. Deploy the adversarial-research skill for high-stakes decisions or when confirmation bias is a risk.

---

## Commands

```bash
# Python environment (uv - required package manager)
uv sync                                         # Install/sync all dependencies
uv run pytest                                   # Run tests via uv
uv add package-name                             # Add new dependency
uv remove package-name                          # Remove dependency
# ⚠️ NEVER use pip install - always use uv sync

# Backend
cd backend-api && uvicorn main:app --reload    # Start API (port 8000)
uv run pytest                                   # Run all tests
uv run pytest tests/unit -v                    # Unit tests only
uv run pytest --cov=src --cov-report=html      # Coverage report

# Frontend
cd frontend && pnpm install                     # Install deps
cd frontend && pnpm dev                         # Dev server (port 5173)
cd frontend && pnpm test                        # Vitest tests
cd frontend && pnpm build                       # Production build

# Database
psql $DATABASE_URL                              # Connect to PostgreSQL
alembic upgrade head                            # Run migrations
alembic revision --autogenerate -m "desc"       # Create migration

# Quality
ruff check . --fix                              # Lint Python
mypy src/                                       # Type check
bandit -r src/                                  # Security scan
```

---

## Project Structure

```
/
├── backend-api/           # FastAPI backend
│   ├── src/
│   │   ├── api/          # Route handlers
│   │   ├── models/       # SQLAlchemy + Pydantic
│   │   ├── services/     # Business logic
│   │   └── db/           # Database layer
│   ├── tests/            # pytest tests (~1,009 tests collected)
│   └── alembic/          # Migrations
├── frontend/              # React 19 + TypeScript
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API clients
│   │   └── types/        # TypeScript types
│   └── tests/            # Vitest tests
├── mcp-server/            # Python MCP server
├── mcp-server-ts/         # TypeScript MCP server
├── .github/
│   ├── agents/           # GitHub Copilot custom agents
│   └── workflows/        # CI/CD (18 workflows)
└── docs/                  # Documentation library (15 docs)
```

---

## Code Style

### TypeScript

```typescript
// Always: explicit types, validation, error handling
interface CreateTaskParams {
  title: string;
  priority?: 'low' | 'medium' | 'high' | 'critical';
}

async function createTask(params: CreateTaskParams): Promise<Task> {
  const validated = CreateTaskSchema.parse(params);

  return db.transaction(async (tx) => {
    const task = await tx.tasks.create(validated);
    await tx.auditLog.create({ action: 'task.created', entityId: task.id });
    return task;
  });
}
```

### Python

```python
# Always: type hints, Pydantic models, async, docstrings
from pydantic import BaseModel, Field

class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    priority: str | None = Field(None, pattern="^(low|medium|high|critical)$")

async def create_task(request: CreateTaskRequest) -> Task:
    """Create task with validation and audit logging.

    Args:
        request: Validated task creation parameters

    Returns:
        Created task instance

    Raises:
        ConflictError: If task_id already exists
    """
    async with db.transaction():
        task = await db.tasks.create(**request.model_dump())
        await db.audit_log.create(action="task.created", entity_id=task.id)
        return task
```

---

## Testing

### Pytest Patterns

```python
# Arrange-Act-Assert pattern
async def test_create_task_success():
    # Arrange
    request = CreateTaskRequest(title="Test Task", priority="high")

    # Act
    result = await create_task(request)

    # Assert
    assert result.title == "Test Task"
    assert result.task_id is not None
    assert result.status == TaskStatus.NEW

# Use fixtures from conftest.py
@pytest.fixture
def sample_task():
    return Task(task_id="TASK-001", title="Sample", status="new")
```

### Coverage Targets (Work Codex)

| Layer | Target | Current |
|-------|--------|---------|
| Unit | ≥70% | 78% |
| Integration | ≥40% | 35% |
| System | ≥25% | 18% |

---

## Database

### PostgreSQL Authority

PostgreSQL is the **single source of truth**. Never cache authoritative data elsewhere.

```sql
-- Table naming: snake_case, plural
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'new',
    priority VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index naming: idx_{table}_{columns}
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
```

### Status Enums (Unified v1.3.0)

**Task Status** (8 states):
```python
TaskStatus = Literal["new", "ready", "active", "in_progress", "blocked", "review", "done", "dropped"]
```

**Sprint/Project Status** (8 states):
```python
SprintStatus = Literal["new", "pending", "assigned", "active", "in_progress", "blocked", "completed", "cancelled"]
ProjectStatus = Literal["new", "pending", "assigned", "active", "in_progress", "blocked", "completed", "cancelled"]
```

**Status-Required Fields**:
- `blocked_reason`: Required when status is `blocked`
- `pending_reason`: Required when status is `pending`

### Phase Tracking

All entities include a `phases` field tracking lifecycle phases:
- **research**: Has research been conducted? Is it adequate?
- **planning**: Are acceptance criteria, DoD, and implementation plan defined?
- **implementation**: Progress percentage, PR status, deployment status
- **testing**: Unit/integration/e2e tests, coverage, QA approval

```python
# Access phase tracking
task.phases.current_phase      # "implementation"
task.phases.all_phases_complete  # False
task.phases.summary()          # {'research': 'completed', ...}
```

---

## Git Workflow

```bash
# Branch naming
feature/TASK-123-description
bugfix/TASK-456-description
hotfix/critical-security-fix

# Commit format (Conventional Commits)
feat(api): add task filtering endpoint
fix(db): handle null priority gracefully
docs(readme): update installation steps
test(tasks): add edge case coverage
refactor(services): extract validation logic

# Before committing
pytest && ruff check . && mypy src/
```

---

## Boundaries

### ✅ Always Do

- Run tests before committing
- Use type hints everywhere
- Handle errors explicitly with context
- Validate all user inputs
- Log state mutations (structured JSONL)
- Search existing code before creating new

### ⚠️ Ask First

- Database schema changes (need migration)
- Breaking API changes (need versioning)
- Adding new dependencies
- Modifying CI/CD workflows
- Changes to .env or secrets

### 🚫 Never Do

- Commit secrets or credentials
- Skip tests for "quick fixes"
- Modify generated files (alembic versions, lock files)
- Push directly to `main`
- Disable security checks or linting
- Create duplicate functionality without checking existing code

---

## MCP Integration

MCP servers configured in `.vscode/mcp.json`:

| Server | Purpose |
|--------|---------|
| github | Repository operations via GitHub CLI |
| filesystem | File access to project directories |
| sequential-thinking | Extended reasoning for complex problems |

---

## API Conventions

```python
# Route pattern: /api/v1/{resource}
@router.get("/tasks/{task_id}")
async def get_task(task_id: str) -> TaskResponse:
    task = await db.tasks.find(task_id)
    if not task:
        raise HTTPException(404, f"Task not found: {task_id}")
    return TaskResponse.model_validate(task)

@router.post("/tasks", status_code=201)
async def create_task(request: CreateTaskRequest) -> TaskResponse:
    task = await task_service.create(request)
    return TaskResponse.model_validate(task)
```

---

## Troubleshooting

```bash
# Database connection issues
psql $DATABASE_URL -c "SELECT 1"

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reset frontend
rm -rf node_modules && pnpm install

# Check for port conflicts
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Reset test database
dropdb taskman_test && createdb taskman_test
alembic upgrade head
```

---

## Context Ontology Framework (COF)

Tasks are analyzed across 13 dimensions. Key dimensions for development:

- **Motivational**: Why does this matter? (business driver)
- **Relational**: How does it connect to other systems?
- **Validation**: How do we prove it works? (tests, evidence)
- **Temporal**: When must it be done? (scheduling)

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start backend | `uvicorn main:app --reload` |
| Start frontend | `pnpm dev` |
| Run all tests | `pytest` |
| Type check | `mypy src/` |
| Lint | `ruff check . --fix` |
| Format | `ruff format .` |
| Security scan | `bandit -r src/` |
| Coverage | `pytest --cov=src` |
| New migration | `alembic revision --autogenerate -m "desc"` |
| Apply migrations | `alembic upgrade head` |

---

**"Trust Nothing, Verify Everything. Evidence is the closing loop of trust."**
