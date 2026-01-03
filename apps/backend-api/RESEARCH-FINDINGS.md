# TaskMan-v2 Backend API Research Findings

**Date**: 2025-11-25
**Agent**: Backend API Research Agent
**Session**: taskman-v2-backend-research

---

## Executive Summary

This document provides a comprehensive analysis of the TaskMan-v2 codebase to inform FastAPI backend implementation. The research covers existing TypeScript MCP server architecture, data models, database patterns, and integration requirements.

---

## 1. Complete Inventory of Existing TaskMan-v2 Components

### 1.1 Directory Structure Overview

```
TaskMan-v2/
├── backend-api/               # ← PLACEHOLDER (this research target)
│   ├── README.md              # Roadmap documentation (147 lines)
│   ├── pyproject.toml.template # Complete dependency & tool config (221 lines)
│   └── .gitkeep
├── mcp-server-ts/             # TypeScript MCP Server (REFERENCE IMPLEMENTATION)
│   ├── src/
│   │   ├── index.ts           # Server entry point with STDIO/HTTP transports
│   │   ├── config/            # Runtime configuration (env.ts)
│   │   ├── core/              # Types, schemas, errors
│   │   │   ├── types.ts       # 373 lines - Complete type definitions
│   │   │   ├── schemas.ts     # 399 lines - Zod validation schemas
│   │   │   └── errors.ts
│   │   ├── features/          # Domain feature modules
│   │   │   ├── tasks/         # Task CRUD + bulk operations
│   │   │   ├── projects/      # Project management + comments/blockers
│   │   │   └── action-lists/  # ActionList management
│   │   ├── backend/           # HTTP client layer (1417 lines)
│   │   │   ├── client.ts      # Axios client with retry logic
│   │   │   └── client-with-circuit-breaker.ts
│   │   ├── infrastructure/    # Cross-cutting concerns
│   │   │   ├── audit.ts       # Audit logging
│   │   │   ├── logger.ts      # Pino structured logging
│   │   │   ├── locking.ts     # Resource locking
│   │   │   ├── cache.ts       # In-memory caching
│   │   │   ├── metrics.ts     # Prometheus metrics
│   │   │   ├── health.ts      # Health check service
│   │   │   └── circuit-breaker.ts
│   │   └── transports/        # MCP transport implementations
│   └── tests/                 # 24 validation scripts + vitest
├── mcp-server-py/             # Python MCP Server (PLANNED)
│   ├── README.md              # 458 lines - Detailed roadmap
│   └── pyproject.toml.template
├── src/                       # React 19 Frontend
├── shared/config/             # Shared configuration
├── docs/                      # CICD, dependency management docs
├── scripts/                   # Utility scripts
└── tests/                     # Playwright E2E tests
```

### 1.2 Component Status Matrix

| Component | Status | Lines of Code | Notes |
|-----------|--------|---------------|-------|
| Frontend (React 19) | ✅ Complete | ~1500+ | Vite, Tailwind, React 19 |
| TypeScript MCP | ✅ Complete | ~4000+ | 40+ MCP tools registered |
| Python MCP | 🚧 Planned | - | README + template only |
| Backend API | 🚧 Planned | - | README + template only |
| Database Schema | ✅ Complete | - | PostgreSQL @ 172.25.14.122 |

---

## 2. Data Model Documentation

### 2.1 Core Entity Types

Based on analysis of `mcp-server-ts/src/core/types.ts` (373 lines):

#### 2.1.1 Enums

```typescript
// Status & State Enums
ProjectStatus: Active | Inactive
SprintStatus: Planned | Active | Completed | Cancelled
TaskStatus: Planned | New | Pending | InProgress | Completed | Blocked | Cancelled
WorkType: Task | Epic | Story | Bug | Feature | Spike
TaskPriority: Low | Medium | High | Critical
ActionListStatus: Planned | New | Pending | Active | InProgress | Blocked | Completed | Archived | Cancelled
ActionListPriority: Low | Medium | High | Critical

// Quality & Risk Enums
Severity: Low | Medium | High | Critical
RiskLevel: Low | Medium | High | Critical
ValidationState: Pending | InProgress | Passed | Failed
Health: Excellent | Good | Fair | Poor | Critical

// ContextForge Enums
GeometryShape: Circle | Triangle | Spiral | Pentagon | Fractal
ShapeStage: Foundation | Growth | Optimization
```

#### 2.1.2 Task Model (70+ fields)

```typescript
interface TaskAttributes {
  // Core Fields
  title: string;                    // Required
  description?: string | null;
  status?: TaskStatus;
  work_type?: WorkType;
  priority?: TaskPriority | null;

  // Ownership & Assignment
  owner?: string | null;
  assignee?: string | null;
  assignees?: string[] | null;
  watchers?: string[] | null;

  // Hierarchy & Relationships
  project_id: string;               // Required
  sprint_id?: string | null;
  parent_task_id?: string | null;
  subtasks?: string[] | null;
  depends_on?: string[] | null;
  blocks?: string[] | null;

  // Time Tracking
  estimated_hours?: number | null;
  actual_hours?: number | null;
  actual_minutes?: number | null;
  due_date?: ISODateTimeString | null;
  done_date?: ISODateTimeString | null;
  target_date?: ISODateTimeString | null;

  // Agile Metrics
  velocity_points?: number | null;
  estimate_points?: number | null;

  // ContextForge Integration
  geometry_shape?: GeometryShape | null;
  shape_stage?: ShapeStage | null;
  validation_state?: ValidationState | null;
  evidence_required?: boolean | null;
  evidence_emitted?: boolean | null;
  context_objects?: string[] | null;
  context_dimensions?: string[] | null;

  // Risk & Quality
  severity?: Severity | null;
  risk_level?: RiskLevel | null;
  risk_notes?: string | null;
  mitigation_status?: string | null;
  last_health?: Health | null;

  // Metadata & Tracing
  tags?: string[] | null;
  attachments?: string[] | null;
  notes?: string | null;
  summary?: string | null;
  completion_notes?: string | null;
  phases?: Record<string, unknown> | null;
  build_manifest?: string | null;

  // Agent & Correlation
  agent_id?: string | null;
  correlation_id?: UUID | null;
  correlation_hint?: string | null;
  batch_id?: string | null;
  content_hash?: string | null;
  origin_source?: string | null;
  load_group?: string | null;

  // Audit & Versioning
  audit_tag?: string | null;
  task_sequence?: number | null;
  schema_version?: string | null;
  verification_requirements?: string | null;
  critical_path?: boolean | null;
  eff_priority?: string | null;

  // Execution Tracking
  execution_trace_log?: Record<string, unknown> | null;
  last_heartbeat_utc?: ISODateTimeString | null;
  aar_count?: number | null;
  last_aar_utc?: ISODateTimeString | null;
  misstep_count?: number | null;
  last_misstep_utc?: ISODateTimeString | null;

  // Soft Delete
  deleted_at?: ISODateTimeString | null;
}

interface TaskRecord extends TaskAttributes {
  id: string;
  status: TaskStatus;
  work_type: WorkType;
  priority: TaskPriority | null | undefined;
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}
```

#### 2.1.3 Project Model

```typescript
interface ProjectAttributes {
  name: string;                     // Required
  description?: string | null;
  status?: ProjectStatus;
}

interface ProjectRecord extends ProjectAttributes {
  id: string;
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}
```

#### 2.1.4 Sprint Model

```typescript
interface SprintAttributes {
  name: string;                     // Required
  description?: string | null;
  status?: SprintStatus;
  project_id: string;               // Required
  start_date?: ISODateTimeString | null;
  end_date?: ISODateTimeString | null;
  actual_start_date?: ISODateTimeString | null;
  actual_end_date?: ISODateTimeString | null;
  capacity_points?: number | null;
  committed_points?: number | null;
  completed_points?: number | null;
  velocity?: number | null;
  goals?: string[] | null;
  retrospective_notes?: string | null;
}

interface SprintRecord extends SprintAttributes {
  id: string;
  created_at: ISODateTimeString;
  updated_at: ISODateTimeString;
}
```

#### 2.1.5 ActionList Model

```typescript
interface ActionListItem {
  id?: string;
  text: string;
  completed?: boolean;
  order?: number;
}

interface ActionListAttributes {
  title: string;                    // Required
  description?: string | null;
  project_id?: string | null;
  sprint_id?: string | null;
  task_id?: string | null;
  status?: ActionListStatus | null;
  priority?: ActionListPriority | null;
  notes?: string | null;
  items?: ActionListItem[] | null;
  metadata?: Record<string, unknown> | null;
}

interface ActionListRecord extends ActionListAttributes {
  id: string;
}
```

#### 2.1.6 Supporting Types

```typescript
// Concurrency Control
interface ConcurrencyMeta {
  token?: string | null;
  etag?: string | null;
  version?: string | null;
  updated_at?: ISODateTimeString | null;
  updated_by?: string | null;
}

// Telemetry
interface TaskTelemetry {
  operation_id: UUID;
  tool_name: string;
  task_id?: string | null;
  started_at: ISODateTimeString;
  finished_at: ISODateTimeString;
  latency_ms: number;
  status_code?: number | null;
  outcome: "success" | "conflict" | "error";
  request_id?: string | null;
  correlation_id?: UUID | null;
  error_code?: string | null;
  retries?: number | null;
}

// Comments & Blockers
interface TaskComment {
  id: string;
  message: string;
  author?: string | null;
  created_at: ISODateTimeString;
  updated_at?: ISODateTimeString | null;
  tags?: string[] | null;
}

interface TaskBlocker {
  id: string;
  description: string;
  severity?: Severity | null;
  status?: string | null;
  created_at: ISODateTimeString;
  resolved_at?: ISODateTimeString | null;
  external_reference?: string | null;
  linked_task_id?: string | null;
}
```

### 2.2 Extended Entity Models (from DATABASE-MODEL-EXPANSION-SUMMARY.md)

The database schema supports 8 entity types:

1. **Project** (~40 fields) - Full ContextForge integration
2. **Sprint** (~30 fields) - ContextForge enhanced
3. **Task** (~70 fields) - Full ContextForge integration
4. **ActionList** (~18 fields) - Lightweight execution containers
5. **MetaTask** (~35 fields) - High-level initiatives/epics
6. **Comment** (~20 fields) - Polymorphic annotations
7. **KBArticle** (~30 fields) - Knowledge base articles
8. **ConfigItem** (~25 fields) - Configuration tracking

---

## 3. TypeScript MCP Server Tools (Parity Requirements)

### 3.1 Task Tools (from `features/tasks/register.ts`)

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `task_create` | Create a new task | `task: TaskAttributes` |
| `task_read` | Get task by ID | `taskId: string` |
| `task_update` | Update task fields | `taskId: string, changes: TaskUpdate` |
| `task_set_status` | Update status + notes | `taskId, status, notes?, completion_notes?, done_date?` |
| `task_assign` | Assign to owner(s) | `taskId, assignee?, assignees?` |
| `task_delete` | Delete a task | `taskId: string` |
| `task_list` | List tasks with filters | `status?, work_type?, priority?, project_id?, sprint_id?, etc.` |
| `task_bulk_update` | Bulk update multiple tasks | `taskIds: string[], changes: TaskUpdate` |
| `task_bulk_assign_sprint` | Assign tasks to sprint | `taskIds: string[], sprintId: string` |
| `task_search` | Full-text search | `query, fields?, project_id?, sprint_id?, skip?, limit?` |

### 3.2 Project Tools (from `features/projects/register.ts`)

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `project_create` | Create new project | `project: ProjectAttributes` |
| `project_read` | Get project by ID | `projectId: string` |
| `project_update` | Update project | `projectId, changes` |
| `project_delete` | Delete project | `projectId: string` |
| `project_list` | List projects | `status?, search?, limit?, cursor?` |
| `project_add_sprint` | Associate sprint | `projectId, sprintId` |
| `project_remove_sprint` | Detach sprint | `projectId, sprintId` |
| `project_add_meta_task` | Add meta task | `projectId, metaTask` |
| `project_add_comment` | Add comment | `projectId, comment` |
| `project_add_blocker` | Add blocker | `projectId, blocker` |
| `project_get_comments` | List comments | `projectId, params?` |
| `project_get_metrics` | Get analytics | `projectId: string` |

### 3.3 ActionList Tools (from `features/action-lists/register.ts`)

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `action_list_create` | Create action list | `ActionListAttributes` |
| `action_list_read` | Get by ID | `actionListId` |
| `action_list_update` | Update action list | `action_list_id, changes` |
| `action_list_delete` | Delete action list | `actionListId` |
| `action_list_list` | List action lists | `status?, priority?, project_id?, etc.` |
| `action_list_add_item` | Add item to list | `action_list_id, text, order?` |
| `action_list_reorder` | Reorder items | `action_list_id, item_ids` |
| `action_list_bulk_delete` | Bulk delete | `action_list_ids` |
| `action_list_bulk_update` | Bulk update | `action_list_ids, changes` |
| `action_list_search` | Search action lists | `q, fields?, project_id?, etc.` |

---

## 4. Integration Points with Existing Systems

### 4.1 Database Configuration

**PostgreSQL Server**: `172.25.14.122:5432/taskman_v2`

**Connection Pattern** (from workspace analysis):
```python
DATABASE_URL=postgresql+asyncpg://user:pass@172.25.14.122:5432/taskman_v2
```

**Required Libraries** (from pyproject.toml.template):
- `sqlalchemy[asyncio]>=2.0,<3.0`
- `asyncpg>=0.30,<1.0`
- `alembic>=1.13,<2.0`

### 4.2 TypeScript MCP → Backend API Communication

The TypeScript MCP server uses `BackendClient` (1417 lines) with:

- **Base URL**: `http://localhost:3001/api/v1` (configurable via `TASK_MANAGER_API_ENDPOINT`)
- **Retry Logic**: Exponential backoff (1s, 2s, 4s) for status codes 429, 500, 503
- **Connection Pooling**: HTTP(S) agents with keepAlive, maxSockets=10
- **Headers**: Content-Type: application/json, x-request-id, x-correlation-id
- **Timeout**: 30 seconds default

**API Envelope Pattern**:
```typescript
interface ApiEnvelope<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
```

### 4.3 Authentication Requirements

From backend-api/README.md:
- JWT validation middleware
- Auth0 integration (OIDC)
- Role-based access control (RBAC)
- API key support for MCP servers

Environment variables:
```
AUTH0_DOMAIN=<your-domain>.auth0.com
AUTH0_AUDIENCE=https://api.taskman-v2.local
SECRET_KEY=<generated-secret>
```

### 4.4 CORS Configuration

```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4.5 Observability Integration

From TypeScript MCP:
- **Metrics**: Prometheus endpoint at `/metrics`
- **Tracing**: OpenTelemetry with OTLP exporter
- **Logging**: Pino structured logging (JSON format)
- **Health Checks**: `/health/live`, `/health/ready`, `/health/startup`

---

## 5. Recommended FastAPI Project Structure

Based on the TypeScript MCP patterns and Python best practices:

```
TaskMan-v2/backend-api/
├── src/
│   └── taskman_api/
│       ├── __init__.py
│       ├── main.py                    # FastAPI app entry point
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py            # Pydantic Settings (env config)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── enums.py               # Status, Priority, WorkType enums
│       │   ├── exceptions.py          # Custom exception classes
│       │   └── security.py            # JWT/Auth0 utilities
│       ├── db/
│       │   ├── __init__.py
│       │   ├── session.py             # AsyncSession factory
│       │   ├── base.py                # SQLAlchemy Base
│       │   └── models/
│       │       ├── __init__.py
│       │       ├── task.py            # Task model (70+ fields)
│       │       ├── project.py         # Project model
│       │       ├── sprint.py          # Sprint model
│       │       └── action_list.py     # ActionList model
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── task.py                # Pydantic schemas (Create, Update, Response)
│       │   ├── project.py
│       │   ├── sprint.py
│       │   └── action_list.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py                # Dependency injection (get_db, get_current_user)
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py          # APIRouter aggregation
│       │       ├── tasks.py           # Task endpoints
│       │       ├── projects.py        # Project endpoints
│       │       ├── sprints.py         # Sprint endpoints
│       │       └── action_lists.py    # ActionList endpoints
│       ├── services/
│       │   ├── __init__.py
│       │   ├── task_service.py        # Business logic layer
│       │   ├── project_service.py
│       │   └── sprint_service.py
│       └── infrastructure/
│           ├── __init__.py
│           ├── logging.py             # Unified logger integration
│           ├── health.py              # Health check handlers
│           └── middleware.py          # Correlation ID, error handling
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # pytest fixtures
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_schemas.py
│   └── integration/
│       ├── test_task_api.py
│       └── test_project_api.py
├── pyproject.toml                     # From template
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 6. API Endpoint Mapping (TypeScript MCP → FastAPI)

### 6.1 Task Endpoints

| MCP Tool | HTTP Method | FastAPI Endpoint |
|----------|-------------|------------------|
| `task_create` | POST | `/api/v1/tasks` |
| `task_read` | GET | `/api/v1/tasks/{task_id}` |
| `task_update` | PATCH | `/api/v1/tasks/{task_id}` |
| `task_set_status` | PATCH | `/api/v1/tasks/{task_id}/status` |
| `task_assign` | PATCH | `/api/v1/tasks/{task_id}/assign` |
| `task_delete` | DELETE | `/api/v1/tasks/{task_id}` |
| `task_list` | GET | `/api/v1/tasks` |
| `task_bulk_update` | PATCH | `/api/v1/tasks/bulk` |
| `task_bulk_assign_sprint` | POST | `/api/v1/tasks/bulk/sprint` |
| `task_search` | POST | `/api/v1/tasks/search` |

### 6.2 Project Endpoints

| MCP Tool | HTTP Method | FastAPI Endpoint |
|----------|-------------|------------------|
| `project_create` | POST | `/api/v1/projects` |
| `project_read` | GET | `/api/v1/projects/{project_id}` |
| `project_update` | PATCH | `/api/v1/projects/{project_id}` |
| `project_delete` | DELETE | `/api/v1/projects/{project_id}` |
| `project_list` | GET | `/api/v1/projects` |
| `project_add_sprint` | POST | `/api/v1/projects/{project_id}/sprints` |
| `project_remove_sprint` | DELETE | `/api/v1/projects/{project_id}/sprints/{sprint_id}` |
| `project_add_comment` | POST | `/api/v1/projects/{project_id}/comments` |
| `project_get_comments` | GET | `/api/v1/projects/{project_id}/comments` |
| `project_add_blocker` | POST | `/api/v1/projects/{project_id}/blockers` |
| `project_get_metrics` | GET | `/api/v1/projects/{project_id}/metrics` |

### 6.3 Sprint Endpoints

| MCP Tool | HTTP Method | FastAPI Endpoint |
|----------|-------------|------------------|
| `sprint_create` | POST | `/api/v1/sprints` |
| `sprint_read` | GET | `/api/v1/sprints/{sprint_id}` |
| `sprint_update` | PATCH | `/api/v1/sprints/{sprint_id}` |
| `sprint_delete` | DELETE | `/api/v1/sprints/{sprint_id}` |
| `sprint_list` | GET | `/api/v1/sprints` |

### 6.4 ActionList Endpoints

| MCP Tool | HTTP Method | FastAPI Endpoint |
|----------|-------------|------------------|
| `action_list_create` | POST | `/api/v1/action-lists` |
| `action_list_read` | GET | `/api/v1/action-lists/{list_id}` |
| `action_list_update` | PATCH | `/api/v1/action-lists/{list_id}` |
| `action_list_delete` | DELETE | `/api/v1/action-lists/{list_id}` |
| `action_list_list` | GET | `/api/v1/action-lists` |
| `action_list_add_item` | POST | `/api/v1/action-lists/{list_id}/items` |
| `action_list_reorder` | PATCH | `/api/v1/action-lists/{list_id}/reorder` |
| `action_list_bulk_delete` | DELETE | `/api/v1/action-lists/bulk` |
| `action_list_bulk_update` | PATCH | `/api/v1/action-lists/bulk` |
| `action_list_search` | POST | `/api/v1/action-lists/search` |

---

## 7. Implementation Priorities

### Phase 1: Foundation (1-2 weeks)
1. FastAPI application scaffold with config
2. SQLAlchemy async models (Task, Project, Sprint)
3. Alembic migrations setup
4. Database session management
5. Health check endpoints (`/health`)

### Phase 2: Core CRUD (2-3 weeks)
1. Task CRUD endpoints with Pydantic schemas
2. Project CRUD endpoints
3. Sprint CRUD endpoints
4. Input validation and error handling
5. Structured logging integration

### Phase 3: Advanced Features (2 weeks)
1. ActionList endpoints
2. Bulk operations
3. Search functionality
4. Comments & blockers

### Phase 4: Authentication (1-2 weeks)
1. JWT validation middleware
2. Auth0 integration
3. RBAC implementation
4. API key support

### Phase 5: Production Hardening (1-2 weeks)
1. Rate limiting
2. CORS configuration
3. Prometheus metrics
4. Load testing

---

## 8. Key Findings & Recommendations

### 8.1 Data Model Complexity

The Task model has 70+ fields with rich ContextForge integration. **Recommendation**: Use SQLAlchemy's column grouping pattern and Pydantic's `model_config` for field categorization.

### 8.2 API Envelope Consistency

TypeScript MCP uses `{ success: boolean, data?: T, error?: string }`. **Recommendation**: Implement this exact pattern in FastAPI for seamless MCP client compatibility.

### 8.3 Validation Schema Parity

Zod schemas in TypeScript should map 1:1 to Pydantic models. **Recommendation**: Use Pydantic v2's strict mode and custom validators for complex fields.

### 8.4 Concurrency Control

TypeScript MCP implements resource locking (`lockingService`). **Recommendation**: Implement optimistic locking via `updated_at` timestamps + ETag headers in FastAPI.

### 8.5 Telemetry Integration

Rich telemetry patterns in TypeScript (correlation IDs, operation tracking). **Recommendation**: Use FastAPI middleware + `contextvar` for request-scoped correlation IDs.

---

## Appendix A: Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@172.25.14.122:5432/taskman_v2

# Authentication
SECRET_KEY=<generated-secret>
AUTH0_DOMAIN=<your-domain>.auth0.com
AUTH0_AUDIENCE=https://api.taskman-v2.local

# Server
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Feature Flags
ENABLE_METRICS=true
ENABLE_TRACING=false
```

---

## Appendix B: File References

| Source File | Lines | Purpose |
|-------------|-------|---------|
| `mcp-server-ts/src/core/types.ts` | 373 | Complete type definitions |
| `mcp-server-ts/src/core/schemas.ts` | 399 | Zod validation schemas |
| `mcp-server-ts/src/backend/client.ts` | 1417 | Backend HTTP client |
| `mcp-server-ts/src/features/tasks/register.ts` | 474 | Task MCP tools |
| `mcp-server-ts/src/features/projects/register.ts` | 428 | Project MCP tools |
| `mcp-server-ts/src/features/action-lists/register.ts` | 492 | ActionList MCP tools |
| `backend-api/README.md` | 147 | Existing roadmap |
| `backend-api/pyproject.toml.template` | 221 | Dependencies & tooling |
| `DATABASE-MODEL-EXPANSION-SUMMARY.md` | 549 | Full schema documentation |

---

*Research completed: 2025-11-25*
*Agent: Backend API Research Agent*
