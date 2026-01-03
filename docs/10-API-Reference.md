# 10 – API Reference

**Status**: Complete
**Version**: 2.0
**Last Updated**: 2025-11-11
**Related**: [01-Overview](01-Overview.md) | [02-Architecture](02-Architecture.md) | [04-Desktop-Application-Architecture](04-Desktop-Application-Architecture.md)

---

## Overview

ContextForge exposes both **CLI commands** and **REST APIs** for task management, context operations, and analytics.

### API Types

1. **CLI Commands** - Primary interface (dbcli, cf_cli, tasks_cli)
2. **REST API** - TaskMan-v2 FastAPI backend
3. **MCP Tools** - AI/LLM integration via Model Context Protocol

---

## CLI Commands

### CF CLI (Recommended)

All operations should use the modular CLI entry point: `python -m cf_core.cli.main`.

#### Task Commands

```bash
# Create task
python -m cf_core.cli.main task create "Implement JWT auth" --priority high --sprint SPRINT-001

# Start task (update status)
python -m cf_core.cli.main task update TASK-001 --status in_progress

# Update task details
python -m cf_core.cli.main task update TASK-001 --assignee user@example.com
```

#### Sprint Commands

```bash
# Create sprint
python -m cf_core.cli.main sprint create "Q1 2025 Sprint" --start 2025-01-01 --end 2025-03-31

# Sprint status
python -m cf_core.cli.main sprint show SPRINT-001 --json
```

#### Project Commands

```bash
# Create project
python -m cf_core.cli.main project create "TaskMan Production" --status active
```

> **Note**: The legacy `dbcli.py` script is deprecated.

---

## REST API (TaskMan-v2)

Base URL: `http://localhost:8000` (development)

### Health Check

**GET /healthz**

```json
{
  "status": "ok"
}
```

### Task Endpoints

#### Create Task

**POST /api/v1/tasks**

```json
{
  "title": "Implement JWT authentication",
  "description": "Add JWT-based auth to TaskMan-v2",
  "status": "new",
  "priority": "high",
  "sprint_id": "SPRINT-001",
  "assignee": "user@example.com",
  "estimated_hours": 16.0
}
```

**Response** (201 Created):
```json
{
  "id": 123,
  "task_id": "TASK-123",
  "title": "Implement JWT authentication",
  "status": "new",
  "created_at": "2025-11-11T18:30:00Z",
  "updated_at": "2025-11-11T18:30:00Z"
}
```

#### Get Task

**GET /api/v1/tasks/{task_id}**

**Response** (200 OK):
```json
{
  "id": 123,
  "task_id": "TASK-123",
  "title": "Implement JWT authentication",
  "description": "Add JWT-based auth to TaskMan-v2",
  "status": "in_progress",
  "priority": "high",
  "sprint_id": "SPRINT-001",
  "assignee": "user@example.com",
  "estimated_hours": 16.0,
  "actual_hours": 8.5,
  "created_at": "2025-11-11T18:30:00Z",
  "updated_at": "2025-11-11T20:45:00Z"
}
```

#### Update Task

**PUT /api/v1/tasks/{task_id}**

```json
{
  "status": "in_progress",
  "actual_hours": 8.5
}
```

**Response** (200 OK):
```json
{
  "id": 123,
  "task_id": "TASK-123",
  "status": "in_progress",
  "actual_hours": 8.5,
  "updated_at": "2025-11-11T20:45:00Z"
}
```

#### Delete Task

**DELETE /api/v1/tasks/{task_id}**

**Response** (204 No Content)

#### List Tasks

**GET /api/v1/tasks**

**Query Parameters**:
- `status` - Filter by status (new, ready, active, in_progress, blocked, review, done, dropped)
- `sprint_id` - Filter by sprint
- `assignee` - Filter by assignee
- `limit` - Pagination limit (default: 50)
- `offset` - Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": 123,
      "task_id": "TASK-123",
      "title": "Implement JWT authentication",
      "status": "in_progress"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### Sprint Endpoints

#### Get Sprint

**GET /api/v1/sprints/{sprint_id}**

**Response** (200 OK):
```json
{
  "id": 1,
  "sprint_id": "SPRINT-001",
  "title": "Q1 2025 Sprint",
  "goal": "Complete P0 critical tasks",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "velocity": 23.5,
  "status": "active"
}
```

### Context Endpoint

#### Get Context

**GET /context**

Returns merged context (DB authoritative overlay on file data).

**Response** (200 OK):
```json
{
  "projects": [
    {
      "id": "PROJ-001",
      "title": "TaskMan Production",
      "status": "active"
    }
  ],
  "sprints": [],
  "tasks": [],
  "documents": []
}
```

---

## MCP Tools (AI Integration)

## MCP Tools (AI Integration)

ContextForge exposes a suite of **12+ MCP Servers** for AI agents. See [config/MCP-SERVERS.md](../config/MCP-SERVERS.md) for the authoritative catalog.

### Key Tools

#### Task Management (TaskMan-v2)
*   `task_create`: Create new tasks.
*   `task_list`: Query tasks with filters.
*   `task_update`: Modify task status/details.
*   `sprint_list` / `sprint_get`: Manage sprints.

#### Development
*   `github_create_issue`: Create GitHub issues.
*   `github_get_file_contents`: Read remote repo files.
*   `read_file` / `write_file`: Local filesystem access (restricted to workspace).

#### Database
*   `query`: Execute SQL against project databases (DuckDB/PostgreSQL/SQLite).

#### Memory
*   `create_entity`: Add knowledge to the graph.
*   `create_relation`: Link entities.

---

## Status Lifecycle Reference

### Task Status Lifecycle

Tasks use an **8-status lifecycle** optimized for development workflows:

| Status | Description | Valid Transitions |
|--------|-------------|-------------------|
| `new` | Task created, not yet ready for work | `ready`, `dropped` |
| `ready` | Task is ready to be worked on | `active`, `in_progress`, `blocked`, `dropped` |
| `active` | Task is assigned and active | `in_progress`, `blocked`, `dropped` |
| `in_progress` | Task is actively being worked on | `review`, `blocked`, `done`, `dropped` |
| `blocked` | Task is blocked by external dependency | `in_progress`, `ready`, `dropped` |
| `review` | Task is in review/QA | `in_progress`, `done`, `dropped` |
| `done` | Task is completed | (terminal) |
| `dropped` | Task was abandoned/cancelled | (terminal) |

**Status Values**: `new`, `ready`, `active`, `in_progress`, `blocked`, `review`, `done`, `dropped`

### Sprint Status Lifecycle

Sprints use an **8-status lifecycle** for sprint management:

| Status | Description | Valid Transitions |
|--------|-------------|-------------------|
| `new` | Sprint created, not yet planned | `pending`, `assigned`, `active`, `cancelled` |
| `pending` | Sprint awaiting resources/approval | `assigned`, `active`, `cancelled` |
| `assigned` | Sprint assigned to team, not started | `active`, `blocked`, `cancelled` |
| `active` | Sprint is in progress | `in_progress`, `blocked`, `completed`, `cancelled` |
| `in_progress` | Sprint work actively underway | `blocked`, `completed`, `cancelled` |
| `blocked` | Sprint blocked by external dependency | `active`, `cancelled` |
| `completed` | Sprint finished successfully | (terminal) |
| `cancelled` | Sprint was cancelled | (terminal) |

**Status Values**: `new`, `pending`, `assigned`, `active`, `in_progress`, `blocked`, `completed`, `cancelled`

**Required Fields**:
- `blocked_reason`: Required when status is `blocked`
- `pending_reason`: Required when status is `pending`
- `completed_at`: Set automatically when status is `completed`

### Project Status Lifecycle

Projects use the same **8-status lifecycle** as Sprints:

| Status | Description | Valid Transitions |
|--------|-------------|-------------------|
| `new` | Project created | `pending`, `assigned`, `active`, `cancelled` |
| `pending` | Project awaiting approval/resources | `assigned`, `active`, `cancelled` |
| `assigned` | Project assigned to owner | `active`, `blocked`, `cancelled` |
| `active` | Project is active | `in_progress`, `blocked`, `completed`, `cancelled` |
| `in_progress` | Project work actively underway | `blocked`, `completed`, `cancelled` |
| `blocked` | Project blocked | `active`, `cancelled` |
| `completed` | Project finished | (terminal) |
| `cancelled` | Project cancelled | (terminal) |

**Status Values**: `new`, `pending`, `assigned`, `active`, `in_progress`, `blocked`, `completed`, `cancelled`

**Required Fields**:
- `blocked_reason`: Required when status is `blocked`
- `pending_reason`: Required when status is `pending`
- `owner`: Required for `assigned`, `active`, `in_progress` statuses
- `completed_at`: Set automatically when status is `completed`

### Sprint Lifecycle API Methods

The MCP server provides dedicated lifecycle methods for Sprint status transitions:

```python
# Start a sprint (new/pending/assigned -> active)
server.start_sprint(sprint_id="S-001")

# Complete a sprint (active/in_progress -> completed)
server.complete_sprint(sprint_id="S-001", notes="Sprint goals achieved")

# Cancel a sprint (any non-terminal -> cancelled)
server.cancel_sprint(sprint_id="S-001", reason="Project priorities changed")

# Block a sprint (active/in_progress -> blocked)
server.block_sprint(sprint_id="S-001", reason="Waiting for external API access")

# Unblock a sprint (blocked -> active)
server.unblock_sprint(sprint_id="S-001")
```

---

## Phase Tracking Reference

All entities (Task, Sprint, Project) include a `phases` field that tracks the lifecycle through research, planning, implementation, and testing phases.

### Phase Status Values

Each phase can have one of these statuses:

| Status | Description |
|--------|-------------|
| `not_started` | Phase has not begun |
| `in_progress` | Phase is currently active |
| `completed` | Phase is finished |
| `skipped` | Phase was intentionally skipped |
| `blocked` | Phase is blocked by external dependency |

### Phase Structure

```json
{
  "phases": {
    "research": {
      "status": "completed",
      "has_research": true,
      "research_adequate": true,
      "research_artifact_ids": ["DOC-001", "DOC-002"],
      "notes": "Research complete",
      "completed_at": "2025-01-15T10:30:00Z"
    },
    "planning": {
      "status": "completed",
      "has_acceptance_criteria": true,
      "has_definition_of_done": true,
      "has_implementation_plan": true,
      "plan_artifact_ids": ["PRD-001"],
      "completed_at": "2025-01-16T14:00:00Z"
    },
    "implementation": {
      "status": "in_progress",
      "progress_pct": 75,
      "has_code_changes": true,
      "has_pull_request": true,
      "pr_merged": false,
      "deployed": false,
      "pr_urls": ["https://github.com/org/repo/pull/123"],
      "started_at": "2025-01-17T09:00:00Z"
    },
    "testing": {
      "status": "not_started",
      "has_unit_tests": false,
      "has_integration_tests": false,
      "has_e2e_tests": false,
      "tests_passing": false,
      "qa_approved": false
    }
  }
}
```

### Research Phase Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | PhaseStatus | Current phase status |
| `has_research` | bool | Whether any research has been conducted |
| `research_adequate` | bool | Whether attached research is adequate |
| `research_artifact_ids` | list[str] | IDs of attached research documents |
| `notes` | str | Research phase notes |
| `completed_at` | datetime | When research was completed |

### Planning Phase Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | PhaseStatus | Current phase status |
| `has_acceptance_criteria` | bool | Whether acceptance criteria are defined |
| `has_definition_of_done` | bool | Whether DoD is defined |
| `has_implementation_plan` | bool | Whether implementation plan exists |
| `plan_artifact_ids` | list[str] | IDs of planning documents |
| `notes` | str | Planning phase notes |
| `completed_at` | datetime | When planning was completed |

### Implementation Phase Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | PhaseStatus | Current phase status |
| `progress_pct` | int | Implementation progress (0-100) |
| `has_code_changes` | bool | Whether code changes exist |
| `has_pull_request` | bool | Whether PR has been created |
| `pr_merged` | bool | Whether PR has been merged |
| `deployed` | bool | Whether changes are deployed |
| `pr_urls` | list[str] | URLs of related pull requests |
| `commit_shas` | list[str] | Related commit SHAs |
| `started_at` | datetime | When implementation started |
| `completed_at` | datetime | When implementation completed |

### Testing Phase Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | PhaseStatus | Current phase status |
| `has_unit_tests` | bool | Whether unit tests exist |
| `has_integration_tests` | bool | Whether integration tests exist |
| `has_e2e_tests` | bool | Whether e2e tests exist |
| `tests_passing` | bool | Whether all tests pass |
| `coverage_pct` | float | Test coverage percentage |
| `has_manual_qa` | bool | Whether manual QA performed |
| `qa_approved` | bool | Whether QA has approved |
| `test_report_url` | str | URL to test report |
| `started_at` | datetime | When testing started |
| `completed_at` | datetime | When testing completed |

### Phase Tracking Helper Properties

```python
# Get the current active phase
task.phases.current_phase  # "implementation"

# Check if all phases are complete
task.phases.all_phases_complete  # False

# Check if any phase is blocked
task.phases.blocked_phase  # None or "planning"

# Get summary of all phase statuses
task.phases.summary()
# {'research': 'completed', 'planning': 'completed',
#  'implementation': 'in_progress', 'testing': 'not_started',
#  'current': 'implementation'}
```

---

## Schemas

### Task Schema (64 Fields)

See [04-Desktop-Application-Architecture.md](04-Desktop-Application-Architecture.md#64-field-task-schema) for complete schema.

**Field Categories**:
1. Identity (5): id, task_id, title, description, task_type
2. Status & State (7): status, priority, severity, health, risk_level, complexity, effort_estimate
3. Relationships (6): parent_task_id, epic_id, sprint_id, project_id, dependencies, related_tasks
4. People (4): assignee, created_by, reporter, stakeholders
5. Temporal (8): created_at, updated_at, start_date, due_date, completed_at, estimated_hours, actual_hours, remaining_hours
6. Business Context (8): business_value, roi_score, customer_impact, strategic_alignment, motivational_context, success_criteria, acceptance_criteria, definition_of_done
7. Technical (10): technical_scope, integration_points, deployment_env, service_topology, performance_targets, algorithm_notes, data_structures, tech_debt_score, refactor_candidate, deprecation_status
8. Quality (8): test_coverage, security_audit_status, accessibility_compliant, evidence_bundle_hash, validation_status, stability_score, completeness_pct, quality_gate_status
9. COF Dimensions (8): cof_motivational, cof_relational, cof_situational, cof_narrative, cof_sacred_geometry, cof_temporal, cof_spatial, cof_holistic

### Sprint Schema

```json
{
  "id": 1,
  "sprint_id": "SPRINT-001",
  "title": "Q1 2025 Sprint",
  "goal": "Complete P0 critical tasks",
  "start_date": "2025-01-01",
  "end_date": "2025-03-31",
  "velocity": 23.5,
  "status": "new | pending | assigned | active | in_progress | blocked | completed | cancelled"
}
```

### Project Schema

```json
{
  "id": 1,
  "project_id": "PROJ-001",
  "title": "TaskMan Production",
  "status": "new | pending | assigned | active | in_progress | blocked | completed | cancelled",
  "created_at": "2025-11-11T00:00:00Z"
}
```

---

## Error Handling

### Standard Error Envelope

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid status transition",
    "details": {
      "field": "status",
      "expected": "in_progress",
      "received": "invalid_status"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Concurrent modification |
| 500 | Server Error | Unexpected error |

---

## Authentication (Planned - P0-005)

**JWT-Based Authentication**:

```http
Authorization: Bearer <jwt_token>
```

**Token Structure**:
```json
{
  "sub": "user@example.com",
  "exp": 1699999999,
  "roles": ["developer", "admin"]
}
```

**See**: TASKMAN-V2-ARCHITECTURE.md lines 682-766 for implementation guide

---

## Versioning Strategy

**Semantic Versioning**:
- **Minor**: Additive endpoints (backward compatible)
- **Major**: Breaking schema changes

**API Version**: `/api/v1/*`

**OpenAPI Spec**: `http://localhost:8000/docs`

---

## Rate Limiting (Planned)

**Planned Limits**:
- 100 requests/minute per API key
- 1,000 requests/hour per API key

**Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699999999
```

---

## Quick Start

### Using CLI

```bash
# Create task
python dbcli.py task create "My Task" --priority high

# View task
python dbcli.py task get TASK-001
```

### Using REST API (curl)

```bash
# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "My Task", "priority": "high"}'

# Get task
curl http://localhost:8000/api/v1/tasks/TASK-001
```

### Using MCP (Claude Code)

```
User: Create a task for implementing JWT authentication
Claude: [Uses create_task MCP tool automatically]
Task created: TASK-123
```

---

## See Also

### Foundation Documents

- [01-Overview.md](01-Overview.md) - System overview
- [02-Architecture.md](02-Architecture.md) - Architecture details
- [04-Desktop-Application-Architecture.md](04-Desktop-Application-Architecture.md) - TaskMan-v2 API

### Implementation Details

- **OpenAPI Spec**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- [dbcli-command-map.md](database/dbcli-command-map.md) - Complete CLI reference

---

**Document Status**: Complete ✅
**Authoritative**: Yes
**Next Review**: 2026-02-11 (quarterly)
**Maintained By**: ContextForge API Team

---

*"Interfaces are context objects: finite entry points into infinite flows."*
