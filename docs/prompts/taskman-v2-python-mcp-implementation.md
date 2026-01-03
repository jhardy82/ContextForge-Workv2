# TaskMan-v2 Python MCP Server Implementation Prompt

**Version**: 1.0
**Mode**: Directive-Only (Agent Discovers & Generates All Code)
**Target**: Production-Grade Python MCP Server with FastMCP

---

## Mission Statement

Build a Python MCP server for TaskMan-v2 that achieves feature parity with the existing TypeScript implementation while following ContextForge quality standards. The implementation must integrate with the existing PostgreSQL database, provide STDIO transport for Claude Desktop integration, and establish comprehensive evidence trails through structured logging.

---

## Authority Sources

Before beginning implementation, study these authoritative workspace documents:

| Document | Path | Purpose |
|----------|------|---------|
| **ContextForge Codex** | `.github/copilot-instructions.md` | Core agent protocols, CF_CLI authority |
| **AGENTS.md** | `AGENTS.md` | Development workflow, transport policy |
| **COF Framework** | `docs/03-Context-Ontology-Framework.md` | 13-dimensional context analysis |
| **Development Guidelines** | `docs/09-Development-Guidelines.md` | Coding standards |
| **Library Research** | `docs/research/modern-python-cli-libraries-research.md` | Recommended libraries with benchmarks |
| **TypeScript MCP Server** | `TaskMan-v2/mcp-server-ts/src/features/` | Reference implementation for tool parity |

---

## Technology Stack (From Research Findings)

Implement using these evaluated libraries (benchmark scores in parentheses):

| Category | Library | Version | Justification |
|----------|---------|---------|---------------|
| **MCP Framework** | FastMCP | 2.7+ (82.4) | Pythonic API, STDIO-first, auto-schema |
| **CLI Framework** | Typer | 0.12+ (86.7) | FastAPI-like ergonomics, type-safe |
| **Terminal UI** | Rich | 13.x (89.8) | Tables, progress bars, panels |
| **Async Runtime** | anyio | 4.x (87.8) | Backend-agnostic structured concurrency |
| **Database** | asyncpg | 0.30+ (83.7) | 2-4x faster than psycopg3, native async |
| **Configuration** | Pydantic Settings | 2.x (76.7) | Type-safe, env vars, validation |
| **Logging** | structlog | 24.x (86.1) | JSONL evidence trails, processors |
| **Testing** | pytest-asyncio | 0.23+ (55.5) | Async test support |
| **Type Checking** | mypy | 1.13+ | Strict mode enforcement |
| **Linting** | ruff | 0.8+ | Fast, comprehensive linting |

---

## Phase 1: Project Scaffold

### Objective
Create the foundational project structure following Python packaging best practices.

### Deliverables

1. **Project Root Structure**
   - Create `taskman-mcp-py/` directory in projects directory
   - Initialize with `pyproject.toml` using modern PEP 517/518 build system
   - Configure all dependencies from technology stack table
   - Set up development dependencies (pytest, mypy, ruff, pre-commit)

2. **Source Package Layout**
   - Create `src/taskman_mcp/` package structure
   - Organize by domain: `models/`, `services/`, `repositories/`, `tools/`
   - Include `__init__.py` files with proper `__all__` exports
   - Create `py.typed` marker for PEP 561 compliance

3. **Configuration Files**
   - `pytest.ini` with asyncio_mode=auto and markers
   - `mypy.ini` or `pyproject.toml` section with strict=true
   - `ruff.toml` with line-length=100, select common rules
   - `.env.example` with all configuration variables

4. **CI/CD Foundation**
   - `.github/workflows/python-mcp.yml` for GitHub Actions
   - Jobs: lint, type-check, test, coverage
   - Matrix testing: Python 3.11, 3.12

### Success Criteria
- [ ] `pip install -e .` succeeds without errors
- [ ] `ruff check .` passes with zero violations
- [ ] `mypy src/` passes in strict mode
- [ ] `pytest --collect-only` discovers test structure

### COF Analysis (Motivational, Resource, Temporal)
Document in project README: Why Python MCP? What resources allocated? Timeline milestones?

---

## Phase 2: Database Layer

### Objective
Implement async PostgreSQL integration with connection pooling and repository pattern.

### Database Context
- **Host**: `172.25.14.122:5432`
- **Database**: `taskman_v2`
- **Pool Size**: 5-20 connections (configurable)
- **Schema Authority**: Existing Alembic migrations in `TaskMan-v2/backend-api/alembic/`

### Deliverables

1. **Connection Management**
   - Implement async connection pool with asyncpg
   - Configure via Pydantic Settings with environment variable support
   - Add health check method returning pool statistics
   - Implement graceful shutdown with connection cleanup

2. **Repository Pattern**
   - Create `BaseRepository` abstract class with common CRUD patterns
   - Implement `TaskRepository` with full CRUD operations
   - Implement `ProjectRepository` for project management
   - Implement `ActionListRepository` for action list features
   - Add `SprintRepository` for sprint management

3. **Query Optimization**
   - Use prepared statements for repeated queries
   - Implement batch operations with `executemany`
   - Add pagination support with cursor-based navigation
   - Include query timeout configuration

4. **Error Handling**
   - Wrap database exceptions with domain-specific errors
   - Log all database operations with structlog
   - Implement retry logic for transient failures

### Success Criteria
- [ ] Connection pool initializes successfully against PostgreSQL
- [ ] All repositories pass unit tests with test database
- [ ] Query performance: <50ms for single record operations
- [ ] Pool statistics available via health check endpoint

### COF Analysis (Computational, Relational, Resource)
Document data structures, query algorithms, and database resource constraints.

---

## Phase 3: MCP Server Core

### Objective
Implement FastMCP server with tool definitions matching TypeScript parity.

### Tool Categories (29 Total from TS Reference)

**Task Tools (11)**:
- `task_create`, `task_read`, `task_update`, `task_delete`
- `task_list`, `task_search`
- `task_set_status`, `task_assign`
- `task_bulk_update`, `task_bulk_assign_sprint`
- `task_add_to_sprint`

**Project Tools (13)**:
- `project_create`, `project_read`, `project_update`, `project_delete`
- `project_list`, `project_search`
- `project_add_tasks`, `project_remove_tasks`
- `project_get_tasks`, `project_get_sprints`
- `project_create_sprint`, `project_archive`, `project_unarchive`

**Action List Tools (5)**:
- `action_list_create`, `action_list_read`, `action_list_update`, `action_list_delete`
- `action_list_add_item`, `action_list_remove_item`, `action_list_reorder_items`

### Deliverables

1. **Server Configuration**
   - Initialize FastMCP server with "TaskMan-v2" identity
   - Configure STDIO transport as default (Claude Desktop)
   - Add HTTP transport option for network deployments
   - Implement lifecycle hooks for startup/shutdown

2. **Tool Implementation**
   - Create each tool with Pydantic model schemas
   - Use `Annotated[Type, Field(...)]` for parameter documentation
   - Return consistent response structure: `{status, data, message}`
   - Include structured error responses with error codes

3. **Resource Definitions**
   - Implement `task://{task_id}` resource pattern
   - Implement `project://{project_id}` resource pattern
   - Add resource listing capability

4. **Validation Layer**
   - Validate all inputs against Pydantic schemas
   - Implement business rule validation (e.g., status transitions)
   - Return validation errors with field-specific messages

### Success Criteria
- [ ] All 29 tools registered and callable via MCP protocol
- [ ] Tool schemas auto-generated and match documentation
- [ ] STDIO transport works with Claude Desktop
- [ ] Response times <100ms for read operations

### COF Analysis (Computational, Emergent, Validation)
Document tool schemas, unexpected edge cases discovered, validation rules.

---

## Phase 4: Structured Logging

### Objective
Implement ≥90% logging coverage following ContextForge evidence trail standards.

### Logging Events (Minimum Required Set)

| Event Type | When | Required Fields |
|------------|------|-----------------|
| `session_start` | Server initialization | session_id, project_id, timestamp |
| `task_start` | Each tool invocation begins | tool_name, correlation_id |
| `decision` | Branching/validation decisions | decision_type, outcome, reason |
| `artifact_touch_batch` | Database reads | record_count, query_type |
| `artifact_emit` | Records created/modified | record_id, size_bytes, hash |
| `warning` | Non-fatal issues | warning_code, message |
| `error` | Failures | error_code, stack_trace |
| `task_end` | Tool invocation completes | duration_ms, outcome |
| `session_summary` | Server shutdown | total_operations, failures, uptime |

### Deliverables

1. **Logger Configuration**
   - Configure structlog with processor pipeline
   - Add TimeStamper with ISO 8601 format
   - Include CallsiteParameterAdder for file/function/line
   - Output JSONL to `logs/taskman-mcp.jsonl`

2. **Context Binding**
   - Bind session_id at server start
   - Bind correlation_id per request
   - Include user context when available

3. **Development Mode**
   - Use Rich ConsoleRenderer in development
   - Use JSONRenderer in production
   - Configure via environment variable

4. **Coverage Verification**
   - Add logging assertions to integration tests
   - Verify ≥90% of execution paths have log events
   - Generate coverage report for logging

### Success Criteria
- [ ] All 9 event types implemented and emitting
- [ ] JSONL output parseable by log analysis tools
- [ ] Development mode shows readable colored output
- [ ] ≥90% logging coverage verified

### COF Analysis (Recursive, Validation, Evidence)
Document feedback loops enabled by logging, validation through evidence trails.

---

## Phase 5: Test Suite

### Objective
Achieve ≥70% code coverage with comprehensive test pyramid.

### Test Categories

| Category | Focus | Tools | Target Coverage |
|----------|-------|-------|-----------------|
| **Unit** | Individual functions/methods | pytest, hypothesis | 80% |
| **Integration** | Repository + Database | pytest-asyncio, testcontainers | 70% |
| **MCP Tools** | FastMCP tool invocations | MCPTestClient | 90% |
| **CLI** | Typer commands | CliRunner | 70% |

### Deliverables

1. **Test Infrastructure**
   - Configure pytest with asyncio_mode=auto
   - Set up fixtures for database pool, services, repositories
   - Implement test database isolation (truncate between tests)
   - Add hypothesis strategies for property-based testing

2. **Unit Tests**
   - Test all Pydantic models with valid/invalid data
   - Test service layer business logic
   - Test configuration loading and validation
   - Test logging output format

3. **Integration Tests**
   - Test repository CRUD operations against PostgreSQL
   - Test transaction rollback on errors
   - Test connection pool behavior under load
   - Test concurrent operation handling

4. **MCP Tool Tests**
   - Test each of 29 tools via MCPTestClient
   - Verify schema compliance of responses
   - Test error handling and validation
   - Test tool interactions (create then read)

5. **CLI Tests** (if CLI implemented)
   - Test command invocations with CliRunner
   - Test help text generation
   - Test error messages and exit codes

### Success Criteria
- [ ] `pytest --cov` reports ≥70% overall coverage
- [ ] All test categories pass in CI/CD
- [ ] No flaky tests (3x consecutive green runs)
- [ ] Performance tests complete in <30 seconds

### COF Analysis (Validation, Recursive, Emergent)
Document test coverage as validation evidence, regression prevention, discovered edge cases.

---

## Phase 6: Documentation & Deployment

### Objective
Create comprehensive documentation and deployment artifacts.

### Deliverables

1. **README.md**
   - Installation instructions (pip, uv, poetry)
   - Configuration guide with all environment variables
   - Quick start for Claude Desktop integration
   - Development setup instructions

2. **API Documentation**
   - Auto-generated tool documentation from schemas
   - Example requests and responses for each tool
   - Error code reference table

3. **Architecture Decision Records**
   - Document why FastMCP over raw SDK
   - Document asyncpg vs psycopg3 decision
   - Document STDIO-first transport strategy

4. **Deployment Artifacts**
   - `Dockerfile` for containerized deployment
   - `docker-compose.yml` for local development
   - Claude Desktop configuration snippet
   - VS Code MCP settings.json snippet

5. **Migration Guide**
   - Steps to switch from TypeScript to Python server
   - Feature comparison table
   - Configuration mapping (TS env vars → Python env vars)

### Success Criteria
- [ ] README enables new developer onboarding in <15 minutes
- [ ] All 29 tools documented with examples
- [ ] Docker image builds and runs successfully
- [ ] Claude Desktop integration verified manually

### COF Analysis (Narrative, Spatial, Holistic)
Document the story of the implementation, deployment topology, and system-wide integration.

---

## Quality Gates (Blocking)

All phases must pass these gates before completion:

| Gate | Tool | Threshold |
|------|------|-----------|
| **Type Safety** | mypy --strict | Zero errors |
| **Linting** | ruff check | Zero violations |
| **Test Coverage** | pytest --cov | ≥70% |
| **Logging Coverage** | Custom metric | ≥90% of paths |
| **Documentation** | Manual review | All tools documented |

---

## COF 13-Dimensional Analysis Requirements

For each phase, document analysis across relevant dimensions:

### Mandatory Dimensions Per Phase

| Phase | Primary Dimensions | Secondary Dimensions |
|-------|-------------------|---------------------|
| Phase 1 | Motivational, Resource, Temporal | Spatial |
| Phase 2 | Computational, Relational, Resource | Situational |
| Phase 3 | Computational, Emergent, Validation | Relational |
| Phase 4 | Recursive, Validation, Sacred Geometry | Emergent |
| Phase 5 | Validation, Recursive, Emergent | Holistic |
| Phase 6 | Narrative, Spatial, Holistic | Integration |

### Sacred Geometry Alignment

Validate implementation against these patterns:

- **Circle (Completeness)**: All 29 tools implemented, all tests pass
- **Triangle (Stability)**: Plan → Execute → Validate cycle for each phase
- **Spiral (Iteration)**: Incremental delivery with feedback loops
- **Golden Ratio (Balance)**: Effort balanced with value delivered
- **Fractal (Modularity)**: Clean module boundaries, composable components

---

## Evidence Trail Requirements

Following ContextForge Codex "Logs First" principle:

1. **Session Logs**: Every MCP session logged with unique ID
2. **Operation Logs**: Every tool invocation logged with correlation ID
3. **Decision Logs**: Every significant decision point documented
4. **Error Logs**: Every failure captured with context for debugging
5. **Artifact Logs**: Every database mutation logged with before/after

Log files location: `logs/taskman-mcp.jsonl`

---

## Anti-Patterns to Avoid

❌ Copying code from TypeScript implementation (discover patterns, don't translate)
❌ Skipping type hints (mypy strict is required)
❌ Hardcoding configuration (use Pydantic Settings)
❌ Synchronous database operations (asyncpg only)
❌ Print statements for logging (structlog only)
❌ Tests without assertions (every test must verify something)
❌ Documentation without examples (show, don't just tell)

---

## Definition of Done

Implementation complete when:

- [ ] All 29 MCP tools implemented and tested
- [ ] Feature parity with TypeScript implementation verified
- [ ] ≥70% test coverage achieved
- [ ] ≥90% logging coverage achieved
- [ ] mypy strict passes with zero errors
- [ ] ruff check passes with zero violations
- [ ] Claude Desktop integration verified manually
- [ ] README enables <15 minute onboarding
- [ ] All ADRs documented for architectural decisions
- [ ] COF 13D analysis completed for all phases
- [ ] Evidence trails demonstrate UCL compliance

---

## Workspace File References

Reference these existing workspace files during implementation:

```
# Authority Sources
.github/copilot-instructions.md          # Core agent protocols
AGENTS.md                                 # Development workflow
docs/03-Context-Ontology-Framework.md    # COF 13D definitions
docs/09-Development-Guidelines.md        # Coding standards

# Research & Analysis
docs/research/modern-python-cli-libraries-research.md  # Library recommendations

# Reference Implementation (TypeScript)
TaskMan-v2/mcp-server-ts/src/features/tasks/register.ts
TaskMan-v2/mcp-server-ts/src/features/projects/register.ts
TaskMan-v2/mcp-server-ts/src/features/action-lists/register.ts

# Database Schema
TaskMan-v2/backend-api/alembic/versions/  # Migration history
TaskMan-v2/backend-api/models/            # SQLAlchemy models

# Configuration Reference
TaskMan-v2/shared/config/taskman-config.schema.json

# Logging Standards
.github/instructions/logging.instructions.md
python/services/unified_logger.py         # Existing logging patterns
```

---

**Implementation Authority**: Agent generates all code based on research findings
**Human Review**: Required for Phase 2 (database) and Phase 3 (MCP tools)
**Target Completion**: 2-3 focused sessions

---

*This prompt follows ContextForge Work Codex v3.0 directive-only format.*
