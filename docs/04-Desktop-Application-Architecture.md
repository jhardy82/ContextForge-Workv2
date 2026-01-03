# 04 – Desktop Application Architecture (TaskMan-v2)

**Status**: Complete
**Version**: 2.0
**Authoritative Source**: [TASKMAN-V2-ARCHITECTURE.md](../projects/P-CFWORK-DOCUMENTATION/TASKMAN-V2-ARCHITECTURE.md)
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [05-Database-Design-Implementation](05-Database-Design-Implementation.md)

---

## Executive Summary

**TaskMan-v2** is a modern full-stack task management system built with **React 19 (frontend)** and **FastAPI (backend)**, managing ContextForge tasks using a comprehensive **64-field schema**. The system demonstrates strong technical architecture with type-safe TypeScript, comprehensive testing, and dual MCP server integration.

### Production Status: 75% Ready

**Complete**:
- ✅ 64-field task schema with 7-status enum
- ✅ React 19 frontend (TypeScript, Vite, TanStack Query)
- ✅ FastAPI backend (Python 3.11+, SQLAlchemy 2.0)
- ✅ PostgreSQL 15+ database with Alembic migrations
- ✅ MCP integration (Python + TypeScript servers)
- ✅ Test infrastructure (E2E, accessibility, performance)

**Blockers** (P0):
- 🚨 **P0-005**: No JWT authentication (documented solution exists)
- 🚨 **P0-006**: No CI/CD pipeline

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19 | UI framework with concurrent features |
| **TypeScript** | 5.x | Type safety and IntelliSense |
| **Vite** | Latest | Fast build tool and dev server |
| **TanStack Query** | v5 | Server state management |
| **Axios** | Latest | HTTP client with interceptors |
| **CSS Modules** | - | Component-scoped styling |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.100+ | Async Python web framework |
| **Pydantic** | 2.x | Data validation and serialization |
| **SQLAlchemy** | 2.0 | ORM with async support |
| **Alembic** | Latest | Database migrations |
| **PostgreSQL** | 15+ | Primary database |
| **SQLite** | - | Development fallback |

### Testing

| Tool | Purpose |
|------|---------|
| **Vitest** | Unit tests for React components |
| **Playwright** | E2E browser testing |
| **axe-core** | Accessibility testing (WCAG 2.1) |
| **Lighthouse** | Performance testing |
| **pytest** | Backend API tests |

### AI Integration

| Component | Purpose |
|-----------|---------|
| **MCP Python Server** | Model Context Protocol for AI tools |
| **MCP TypeScript Server** | Alternative MCP implementation |
| **Claude Code Integration** | VSCode extension support |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   USER INTERFACES                        │
├─────────────────────────────────────────────────────────┤
│  Web Browser (React 19 + TypeScript)                    │
│  └─ TaskMan-v2 SPA                                      │
│     ├─ Task List View                                   │
│     ├─ Task Detail View                                 │
│     ├─ Task Creation Form                               │
│     └─ Kanban Board View                                │
│                                                          │
│  AI/LLM Interfaces (via MCP)                            │
│  └─ Claude Code Extension                               │
│     └─ VSCode Integration                               │
└─────────────────────────────────────────────────────────┘
                         ↓ HTTPS
┌─────────────────────────────────────────────────────────┐
│                  API GATEWAY LAYER                       │
├─────────────────────────────────────────────────────────┤
│  FastAPI Backend (Python 3.11+)                         │
│  ├─ /api/v1/tasks/* - Task CRUD operations             │
│  ├─ /api/v1/sprints/* - Sprint management              │
│  ├─ /api/v1/projects/* - Project management            │
│  ├─ /docs - Swagger UI (OpenAPI)                       │
│  └─ /redoc - ReDoc documentation                        │
│                                                          │
│  MCP Servers (Model Context Protocol)                   │
│  ├─ Python MCP Server (36/36 tests passing)            │
│  └─ TypeScript MCP Server (alternative)                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 BUSINESS LOGIC LAYER                     │
├─────────────────────────────────────────────────────────┤
│  cf_core Domain Models (DDD)                            │
│  ├─ Task Entity (64-field schema)                      │
│  ├─ Sprint Entity                                       │
│  ├─ Project Entity                                      │
│  └─ Repository Pattern                                  │
│                                                          │
│  Validation Layer (Pydantic)                            │
│  └─ 7-status enum: planned, new, pending,              │
│     in_progress, completed, blocked, cancelled          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                     DATA LAYER                           │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL 15+ (Production)                            │
│  ├─ Host: WSL 172.25.14.122:5432                       │
│  ├─ Database: taskman_v2                                │
│  └─ Alembic Migrations                                  │
│                                                          │
│  SQLite (Development Fallback)                          │
│  └─ Local: db/taskman.sqlite                           │
└─────────────────────────────────────────────────────────┘
```

---

## Frontend Architecture

### Directory Structure

```
TaskMan-v2/
├── src/
│   ├── components/          # React components
│   │   ├── TaskList/       # Task listing with filters
│   │   ├── TaskDetail/     # Single task view
│   │   ├── TaskForm/       # Create/Edit form
│   │   ├── KanbanBoard/    # Drag-and-drop Kanban
│   │   └── common/         # Shared UI
│   ├── hooks/              # Custom React hooks
│   │   ├── useTask.ts      # Task CRUD
│   │   ├── useSprint.ts    # Sprint operations
│   │   └── useAuth.ts      # Auth (TODO: P0-005)
│   ├── services/           # API clients
│   │   ├── taskService.ts  # Task API
│   │   ├── sprintService.ts# Sprint API
│   │   └── api.ts          # Axios instance
│   ├── types/              # TypeScript definitions
│   │   ├── task.ts         # Task types (64 fields)
│   │   ├── sprint.ts       # Sprint types
│   │   └── api.ts          # API response types
│   ├── utils/              # Utilities
│   └── App.tsx             # Root component
├── tests/
│   ├── unit/              # Vitest tests
│   ├── e2e/               # Playwright tests
│   ├── a11y/              # Accessibility tests
│   └── performance/       # Lighthouse tests
├── vite.config.ts
└── package.json
```

### Key Patterns

#### 1. Custom Hooks (TanStack Query)

**`src/hooks/useTask.ts`**:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskService } from '../services/taskService';

export function useTask(taskId: string) {
  return useQuery({
    queryKey: ['task', taskId],
    queryFn: () => taskService.getTask(taskId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (task: TaskCreate) => taskService.createTask(task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}
```

#### 2. Type-Safe API Service

**`src/services/taskService.ts`**:
```typescript
import { api } from './api';
import { Task, TaskCreate, TaskUpdate } from '../types/task';

export const taskService = {
  async getTasks(filters?: TaskFilters): Promise<TaskListResponse> {
    const { data } = await api.get('/api/v1/tasks', { params: filters });
    return data;
  },

  async getTask(id: string): Promise<Task> {
    const { data } = await api.get(`/api/v1/tasks/${id}`);
    return data;
  },

  async createTask(task: TaskCreate): Promise<Task> {
    const { data } = await api.post('/api/v1/tasks', task);
    return data;
  },

  async updateTask(id: string, task: TaskUpdate): Promise<Task> {
    const { data } = await api.put(`/api/v1/tasks/${id}`, task);
    return data;
  },
};
```

---

## Backend Architecture

### Directory Structure

```
TaskMan-v2/backend-api/
├── routers/                # API routes
│   ├── tasks.py           # Task CRUD
│   ├── sprints.py         # Sprint management
│   ├── projects.py        # Project management
│   └── health.py          # Health checks
├── models/                # SQLAlchemy ORM
│   ├── task.py            # Task model
│   ├── sprint.py          # Sprint model
│   └── project.py         # Project model
├── schemas/               # Pydantic schemas
│   ├── task.py            # Validation schemas
│   ├── sprint.py
│   └── project.py
├── dependencies/          # FastAPI deps
│   ├── database.py        # DB session
│   └── auth.py            # Auth (TODO: P0-005)
├── services/              # Business logic
│   ├── task_service.py
│   └── sprint_service.py
├── migrations/            # Alembic
│   └── versions/
├── tests/
├── main.py                # App entry point
└── requirements.txt
```

### FastAPI Endpoints

#### Task CRUD API

**`backend-api/routers/tasks.py`**:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies.database import get_db
from ..schemas.task import TaskCreate, TaskUpdate, TaskResponse
from ..services.task_service import TaskService

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """Create a new task"""
    service = TaskService(db)
    return service.create_task(task)

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get task by ID"""
    service = TaskService(db)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task: TaskUpdate,
    db: Session = Depends(get_db)
):
    """Update task"""
    service = TaskService(db)
    return service.update_task(task_id, task)

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Delete task"""
    service = TaskService(db)
    service.delete_task(task_id)
```

---

## 64-Field Task Schema

### Task Entity Definition

**Field Categories**:

1. **Identity** (5 fields): id, task_id, title, description, task_type
2. **Status & State** (7 fields): status, priority, severity, health, risk_level, complexity, effort_estimate
3. **Relationships** (6 fields): parent_task_id, epic_id, sprint_id, project_id, dependencies, related_tasks
4. **People** (4 fields): assignee, created_by, reporter, stakeholders
5. **Temporal** (8 fields): created_at, updated_at, start_date, due_date, completed_at, estimated_hours, actual_hours, remaining_hours
6. **Business Context** (8 fields): business_value, roi_score, customer_impact, strategic_alignment, motivational_context, success_criteria, acceptance_criteria, definition_of_done
7. **Technical** (10 fields): technical_scope, integration_points, deployment_env, service_topology, performance_targets, algorithm_notes, data_structures, tech_debt_score, refactor_candidate, deprecation_status
8. **Quality** (8 fields): test_coverage, security_audit_status, accessibility_compliant, evidence_bundle_hash, validation_status, stability_score, completeness_pct, quality_gate_status
9. **COF Dimensions** (8 fields): cof_motivational, cof_relational, cof_situational, cof_narrative, cof_sacred_geometry, cof_temporal, cof_spatial, cof_holistic

### Pydantic Schema

**`backend-api/schemas/task.py`**:
```python
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PLANNED = "planned"
    NEW = "new"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    status: TaskStatus = TaskStatus.NEW
    priority: str | None = Field(None, pattern="^(low|medium|high|critical)$")
    sprint_id: str | None = None
    assignee: str | None = None
    estimated_hours: float | None = Field(None, ge=0)
    # ... (64 fields total)

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    # ... (partial update fields)

class TaskResponse(BaseModel):
    id: int
    task_id: str
    title: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    # ... (all 64 fields for response)

    class Config:
        from_attributes = True
```

---

## MCP Integration

### Model Context Protocol (MCP)

MCP enables AI/LLM integration with ContextForge tooling.

#### Python MCP Server

**Location**: `mcp-server/`

**Tools Provided**:
- `create_task` - Create new task
- `get_task` - Fetch task by ID
- `update_task` - Update task fields
- `list_tasks` - Query tasks with filters
- `get_sprint` - Fetch sprint details
- `list_sprints` - Query sprints

**Status**: 36/36 tests passing ✅

#### TypeScript MCP Server

**Location**: `mcp-server-ts/`

**Alternative implementation** with TypeScript for Node.js environments.

### VSCode Integration

**`.vscode/mcp.json`** configuration enables Claude Code to use MCP tools directly in VSCode.

---

## Database Schema

### PostgreSQL Tables

#### tasks table

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL,  -- 7-status enum
    priority VARCHAR(20),
    sprint_id VARCHAR(50),
    assignee VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    -- ... (64 fields total)
    FOREIGN KEY (sprint_id) REFERENCES sprints(sprint_id)
);
```

#### sprints table

```sql
CREATE TABLE sprints (
    id SERIAL PRIMARY KEY,
    sprint_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    goal TEXT,
    start_date DATE,
    end_date DATE,
    velocity FLOAT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Migration: 7-Status Fix

**Migration**: `48b01bf7ee65_add_new_pending_statuses.py`

**Applied**: 2025-10-18 ✅

**Changes**:
- Added `new`, `pending` statuses to enum
- Updated validation constraints
- Backfilled existing data

---

## Testing Strategy

### Test Pyramid

```
            ┌──────────┐
            │   E2E    │  5% - Playwright (critical flows)
            └──────────┘
          ┌──────────────┐
          │ Integration  │  20% - API + DB tests
          └──────────────┘
       ┌───────────────────┐
       │  Component Tests  │  35% - React components
       └───────────────────┘
    ┌──────────────────────────┐
    │     Unit Tests           │  40% - Utilities, services
    └──────────────────────────┘
```

### Test Types

#### 1. Unit Tests (Vitest)

```typescript
// tests/unit/services/taskService.test.ts
import { describe, it, expect, vi } from 'vitest';
import { taskService } from '@/services/taskService';

describe('taskService', () => {
  it('should fetch task by ID', async () => {
    const task = await taskService.getTask('TASK-001');
    expect(task.task_id).toBe('TASK-001');
  });
});
```

#### 2. E2E Tests (Playwright)

```typescript
// tests/e2e/task-creation.spec.ts
import { test, expect } from '@playwright/test';

test('create new task', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.click('[data-testid="create-task-button"]');
  await page.fill('[name="title"]', 'Test Task');
  await page.click('[type="submit"]');
  await expect(page.locator('[data-testid="task-list"]')).toContainText('Test Task');
});
```

#### 3. Accessibility Tests (axe-core)

```typescript
// tests/a11y/task-list.spec.ts
import { test } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test('task list is accessible', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await injectAxe(page);
  await checkA11y(page, null, {
    detailedReport: true,
    detailedReportOptions: { html: true },
  });
});
```

#### 4. Performance Tests (Lighthouse)

```typescript
// tests/performance/lighthouse.spec.ts
import lighthouse from 'lighthouse';

test('performance score > 90', async () => {
  const result = await lighthouse('http://localhost:5173');
  expect(result.lhr.categories.performance.score).toBeGreaterThan(0.9);
});
```

---

## Deployment Architecture

### Development

```bash
# Frontend (Vite dev server)
cd TaskMan-v2
npm run dev  # http://localhost:5173

# Backend (Uvicorn)
cd TaskMan-v2/backend-api
uvicorn main:app --reload  # http://localhost:8000
```

### Production (Planned - P0-006)

**Frontend**: Vercel or Netlify
- Build: `npm run build`
- Deploy: Static assets to CDN

**Backend**: Google Cloud Run or AWS Lambda
- Containerize with Docker
- Deploy FastAPI as serverless function

**Database**: Managed PostgreSQL
- AWS RDS or Google Cloud SQL
- Automated backups, scaling

---

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+ (or SQLite for dev)

### Setup

```bash
# Clone and setup frontend
cd TaskMan-v2
npm install
cp .env.example .env
npm run dev

# Setup backend (separate terminal)
cd TaskMan-v2/backend-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Run migrations
alembic upgrade head

# Start backend
uvicorn main:app --reload
```

### Access

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## See Also

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview
- [02-Architecture.md](02-Architecture.md) - Overall architecture
- [05-Database-Design-Implementation.md](05-Database-Design-Implementation.md) - Database details

### Implementation Details

- [projects/P-CFWORK-DOCUMENTATION/TASKMAN-V2-ARCHITECTURE.md](../projects/P-CFWORK-DOCUMENTATION/TASKMAN-V2-ARCHITECTURE.md) - Complete analysis (1,139 lines)
- [cf_core/README.md](../cf_core/README.md) - Domain-driven design patterns

### Production Blockers

- **P0-005**: JWT Authentication - See TASKMAN-V2-ARCHITECTURE.md lines 682-766 for implementation guide
- **P0-006**: CI/CD Pipeline - See lines 769-863 for GitHub Actions workflows

---

**Document Status**: Complete ✅
**Authoritative**: Yes (sourced from TASKMAN-V2-ARCHITECTURE.md)
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge Application Team

---

*"TaskMan-v2: Modern task management with COF 13D integration, ready for production with P0-005 and P0-006 completion."*
