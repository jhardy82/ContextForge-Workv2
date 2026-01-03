## MCP Tools Reference (TaskMan TypeScript MCP)

Last updated: 2025-12-05
Project: P-TASKMAN-MCP-TYPESCRIPT
Related: docs/api/README.md (TypeDoc), src/core/schemas.ts, src/core/types.ts

### Purpose
This document catalogs the available MCP tools exposed by the TaskMan TypeScript MCP server, their parameters, structured responses, error semantics, and quick usage examples. It is designed to be resumable and extensible as new tools are added.

### How to Use
- Prefer structuredContent responses for programmatic consumption.
- Check `isError: true` and `errorCode` fields for tool-level errors (distinct from protocol errors).
- Validate input against Zod schemas in `src/core/schemas.ts`.

---

## Tool Index (40 Tools Total)

### Activation Tools (4)
1. `activate_taskman_server` - Check server status and list all available tools
2. `activate_task_tools` - Prepare task management tools with status check
3. `activate_project_tools` - Prepare project management tools with status check
4. `activate_action_list_tools` - Prepare action list tools with status check

### Project Tools (13)
5. `project_create` - Create a new project record
6. `project_read` - Retrieve a project by ID
7. `project_update` - Update an existing project
8. `project_delete` - Delete a project and release locks
9. `project_list` - List projects with optional filters
10. `project_add_sprint` - Associate a sprint with a project
11. `project_remove_sprint` - Detach a sprint from a project
12. `project_add_meta_task` - Create a meta task scoped to a project
13. `project_add_comment` - Attach a comment to a project
14. `project_add_blocker` - Record a blocker for a project
15. `project_get_comments` - Retrieve comments attached to a project
16. `project_get_metrics` - Retrieve metrics/analytics for a project

### Task Tools (10)
17. `task_create` - Create a new task record
18. `task_read` - Retrieve a task by ID
19. `task_update` - Update an existing task
20. `task_delete` - Delete a task and release locks
21. `task_list` - List tasks with optional filters
22. `task_set_status` - Update task status with completion notes
23. `task_assign` - Assign task to one or more users
24. `task_bulk_update` - Apply changes to multiple tasks at once
25. `task_bulk_assign_sprint` - Assign multiple tasks to a sprint
26. `task_search` - Search tasks across multiple fields

### Action List Tools (13)
27. `action_list_create` - Create a new action list
28. `action_list_read` - Retrieve an action list by ID
29. `action_list_update` - Update action list properties
30. `action_list_delete` - Permanently delete an action list
31. `action_list_list` - List action lists with filtering
32. `action_list_add_item` - Add an item to an action list
33. `action_list_toggle_item` - Toggle item completion (completed ↔ pending)
34. `action_list_remove_item` - Remove an item from an action list
35. `action_list_reorder_items` - Reorder items by providing item ID sequence
36. `action_list_bulk_delete` - Delete multiple action lists at once
37. `action_list_bulk_update` - Update multiple action lists with same changes
38. `action_list_search` - Search action lists with advanced filtering

> **Note**: Tool names use underscore naming convention (`entity_action`).
> Source: `TaskMan-v2/mcp-server-ts/src/features/*/register.ts`

---

## Common Patterns

- Success response:
  - `content: [{ type: "text", text: JSON.stringify(result) }]`
  - `structuredContent: result` (preferred)

- Error response (tool error):
  - `{ isError: true, errorCode: "NotFound" | "ValidationError" | "BackendUnavailable" | ..., message: string }`

- Concurrency:
  - `concurrencyMeta` payload (ETag/version) used in updates to prevent overwrite.
  - Pattern: pass `version` or `etag` from last read; server rejects stale updates with `ConflictError`.
  - On conflict, re-fetch entity, merge changes, retry with updated `concurrencyMeta`.

---

## Projects

### project_list
List projects with optional filters.

**Parameters** (all optional):
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | `ProjectStatus` | Filter by status: `planning`, `active`, `on_hold`, `completed`, `cancelled` |
| `search` | `string` | Text search in project fields |
| `limit` | `number` | Max results (1-100) |
| `cursor` | `string` | Pagination cursor |

**Returns**: `{ projects: ProjectRecord[] }`

**Errors**: `BackendUnavailableError`, `TimeoutError`

**Example**:
```json
tool: project_list
args: { "status": "active", "limit": 10 }
result: { "projects": [{ "id": "P-001", "title": "TaskMan MCP", "status": "active", ... }] }
```

---

### project_read
Retrieve a project by its identifier.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Project identifier |

**Returns**: `{ project: ProjectRecord }` or error with `errorCode: "NotFound"`

---

### project_create
Create a new project record.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project` | `ProjectCreate` | Yes | Project data per `projectSchema` |

**Returns**: `{ project: ProjectRecord }` (newly created)

**Errors**: `ValidationError`, `ConflictError`

---

### project_update
Update an existing project (with locking).

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Project to update |
| `changes` | `ProjectUpdate` | Yes | Partial update payload |

**Returns**: `{ project: ProjectRecord }` (updated)

**Errors**: `ConflictError` (locked by another agent), `ValidationError`

---

### project_delete
Delete a project and release related locks.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Project to delete |

**Returns**: `{ projectId: string, deleted: true }`

**Errors**: `NotFoundError`, `BackendError`

---

### project_add_sprint
Associate a sprint with a project.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Target project |
| `sprintId` | `string` | Yes | Sprint to associate |

**Returns**: `{ project: ProjectRecord }`

---

### project_remove_sprint
Detach a sprint from the project.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Target project |
| `sprintId` | `string` | Yes | Sprint to remove |

**Returns**: `{ projectId, sprintId, project: ProjectRecord | null }`

---

### project_add_meta_task
Create a meta task scoped to a project.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Target project |
| `metaTask` | `object` | Yes | `{ title, description?, owner?, due_date? }` |

**Returns**: `{ projectId, metaTask: object }`

---

### project_add_comment
Attach a comment to a project.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Target project |
| `comment` | `object` | Yes | `{ message, author?, tags? }` |

**Returns**: `{ projectId, comment: object }`

---

### project_add_blocker
Record a blocker for a project.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Target project |
| `blocker` | `object` | Yes | `{ title, description?, severity?, linked_task_id?, external_reference? }` |

**Returns**: `{ projectId, blocker: object }`

---

### project_get_comments
Retrieve comments attached to a project.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Target project |
| `params` | `object` | No | `{ limit?, cursor? }` for pagination |

**Returns**: `{ projectId, comments: object[] }`

---

### project_get_metrics
Retrieve analytics/metrics for a project.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `projectId` | `string` | Yes | Target project |

**Returns**: `{ projectId, metrics: ProjectAnalytics }`

---

## Tasks

### task_list
List tasks with optional filters.

**Parameters** (all optional):
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | `TaskStatus` | `pending`, `in_progress`, `completed`, `blocked`, `cancelled` |
| `work_type` | `WorkType` | Task work type classification |
| `priority` | `TaskPriority` | `low`, `medium`, `high`, `urgent` |
| `owner` | `string` | Filter by owner |
| `assignee` | `string` | Filter by assignee |
| `project_id` | `string` | Filter by project |
| `sprint_id` | `string` | Filter by sprint |
| `search` | `string` | Text search |
| `tags` | `string[]` | Filter by tags (max 25) |
| `geometry_shape` | `GeometryShape` | Shape classification |
| `shape_stage` | `ShapeStage` | Shape stage |
| `risk_level` | `RiskLevel` | Risk classification |
| `validation_state` | `ValidationState` | Validation status |
| `critical_path` | `boolean` | Is on critical path |
| `evidence_required` | `boolean` | Requires evidence |
| `include_deleted` | `boolean` | Include soft-deleted tasks |
| `limit` | `number` | Max results (1-100) |
| `cursor` | `string` | Pagination cursor |

**Returns**: `{ tasks: TaskRecord[] }`

---

### task_read
Retrieve a task by its identifier.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string` | Yes | Task identifier |

**Returns**: `{ task: TaskRecord }`

---

### task_create
Create a new task record.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task` | `TaskCreate` | Yes | Task data per `taskSchema` |

**Returns**: `{ task: TaskRecord }`

**Example**:
```json
tool: task_create
args: {
  "task": {
    "title": "Write MCP Tools Reference",
    "work_type": "documentation",
    "priority": "high",
    "assignee": "jhardy",
    "project_id": "P-TASKMAN-MCP",
    "tags": ["docs", "mcp"],
    "due_date": "2025-12-10T23:59:00Z"
  }
}
```

---

### task_update
Update an existing task (with locking).

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string` | Yes | Task to update |
| `changes` | `TaskUpdate` | Yes | Partial update (at least one field) |

**Returns**: `{ task: TaskRecord }`

---

### task_delete
Delete a task and release related locks.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string` | Yes | Task to delete |

**Returns**: `{ taskId: string, deleted: true }`

---

### task_set_status
Update the status of a task with optional completion notes.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string` | Yes | Task to update |
| `status` | `TaskStatus` | Yes | New status |
| `notes` | `string` | No | Status change notes |
| `completion_notes` | `string` | No | Completion details |
| `done_date` | `string` | No | ISO datetime when done |

**Returns**: `{ task: TaskRecord }`

---

### task_assign
Assign or reassign a task to one or more owners.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string` | Yes | Task to assign |
| `assignee` | `string?` | Either | Single assignee (nullable to unassign) |
| `assignees` | `string[]` | Either | Multiple assignees |

> At least one of `assignee` or `assignees` must be provided.

**Returns**: `{ task: TaskRecord }`

---

### task_bulk_update
Apply the same changes to multiple tasks at once.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskIds` | `string[]` | Yes | Tasks to update (min 1) |
| `changes` | `TaskUpdate` | Yes | Changes to apply to all |

**Returns**: `{ success: true, updated_count: number, task_ids: string[] }`

---

### task_bulk_assign_sprint
Assign multiple tasks to a sprint in one operation.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskIds` | `string[]` | Yes | Tasks to assign (min 1) |
| `sprintId` | `string` | Yes | Target sprint |

**Returns**: `{ success: true, assigned_count: number, sprint_id: string }`

---

### task_search
Search tasks across multiple fields using query filters.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `string` | Yes | Search query |
| `fields` | `string[]` | No | Fields to search: `title`, `description`, `tags`, `notes`, `summary`, `completion_notes` |
| `project_id` | `string` | No | Limit to project |
| `sprint_id` | `string` | No | Limit to sprint |
| `skip` | `number` | No | Pagination offset |
| `limit` | `number` | No | Max results (1-500) |

**Returns**: `{ success: true, query: string, count: number, tasks: TaskRecord[] }`

---

## Action Lists

### action_list_list
List action lists with optional filtering.

**Parameters** (all optional):
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | `ActionListStatus` | Filter by status |
| `priority` | `ActionListPriority` | Filter by priority |
| `owner` | `string` | Filter by owner |
| `project_id` | `string` | Filter by project |
| `sprint_id` | `string` | Filter by sprint |
| `tags` | `string[]` | Filter by tags (max 25) |
| `limit` | `number` | Max results (1-100) |
| `cursor` | `string` | Pagination cursor |

**Returns**: `{ action_lists: ActionListRecord[] }`

---

### action_list_read
Retrieve an action list by its identifier.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_id` | `string` | Yes | Action list identifier |

**Returns**: `{ action_list: ActionListRecord }`

---

### action_list_create
Create a new action list with optional project/sprint association.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| (input) | `ActionListCreate` | Yes | Action list data per `actionListSchema` |

**Returns**: `{ action_list: ActionListRecord }`

---

### action_list_update
Update an action list's properties (with locking).

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_id` | `string` | Yes | Action list to update |
| (changes) | `ActionListUpdate` | Yes | At least one field required |

**Returns**: `{ action_list: ActionListRecord }`

---

### action_list_delete
Permanently delete an action list and all its items.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_id` | `string` | Yes | Action list to delete |

**Returns**: `{ success: boolean }`

---

### action_list_add_item
Add a new item to an action list.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_id` | `string` | Yes | Target action list |
| `text` | `string` | Yes | Item text |
| `order` | `number` | No | Position in list (0-indexed) |

**Returns**: `{ action_list: ActionListRecord }` (with new item)

---

### action_list_toggle_item
Toggle the completion state of an item (completed ↔ pending).

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_id` | `string` | Yes | Target action list |
| `item_id` | `string` | Yes | Item to toggle |

**Returns**: `{ action_list: ActionListRecord }`

**Example**:
```json
tool: action_list_toggle_item
args: { "action_list_id": "AL-001", "item_id": "AL-ITEM-05" }
```

---

### action_list_remove_item
Remove an item from an action list.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_id` | `string` | Yes | Target action list |
| `item_id` | `string` | Yes | Item to remove |

**Returns**: `{ action_list: ActionListRecord }`

---

### action_list_reorder_items
Reorder items in an action list by providing the desired sequence.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_id` | `string` | Yes | Target action list |
| `item_ids` | `string[]` | Yes | Ordered item IDs (min 1) |

**Returns**: `{ action_list: ActionListRecord }`

---

### action_list_bulk_delete
Delete multiple action lists in a single operation.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_ids` | `string[]` | Yes | Action lists to delete (min 1) |

**Returns**: `{ success: boolean, deleted_count: number }`

---

### action_list_bulk_update
Update multiple action lists with the same changes.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action_list_ids` | `string[]` | Yes | Action lists to update (min 1) |
| `status` | `ActionListStatus` | No | New status |
| `priority` | `ActionListPriority` | No | New priority |
| `project_id` | `string` | No | Assign to project |
| `sprint_id` | `string` | No | Assign to sprint |
| `notes` | `string` | No | Update notes |

> At least one update field must be provided.

**Returns**: `{ success: boolean, updated_count: number, action_list_ids: string[] }`

---

### action_list_search
Search action lists with advanced filtering and pagination.

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | `string` | Yes | Search query |
| `fields` | `string[]` | No | Fields to search: `title`, `description`, `notes` |
| `project_id` | `string` | No | Limit to project |
| `sprint_id` | `string` | No | Limit to sprint |
| `status` | `ActionListStatus` | No | Filter by status |
| `priority` | `ActionListPriority` | No | Filter by priority |
| `skip` | `number` | No | Pagination offset |
| `limit` | `number` | No | Max results (1-100) |

**Returns**: `{ success: boolean, query: string, count: number, data: ActionListRecord[] }`

---

## Activation Tools

These tools check the TaskMan backend API server status before performing operations. Call them first to verify connectivity.

### activate_taskman_server
Check server status and list all available tools. **Call this first before using any tools.**

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `verbose` | `boolean` | No | Include detailed tool descriptions |

**Returns**:
```typescript
{
  serverStatus: {
    serverOnline: boolean,
    apiEndpoint: string,
    latencyMs: number | null,
    message: string,
    startupInstructions?: string[]
  },
  allTools: {
    tasks: string[],
    projects: string[],
    actionLists: string[]
  },
  ready: boolean,
  toolDescriptions?: { ... }  // if verbose=true
}
```

---

### activate_task_tools
Prepare task management tools with status check.

**Parameters**: None

**Returns**: `{ activated: boolean, serverStatus, availableTools: string[], toolDescriptions, nextSteps?: string[] }`

---

### activate_project_tools
Prepare project management tools with status check.

**Parameters**: None

**Returns**: `{ activated: boolean, serverStatus, availableTools: string[], toolDescriptions, nextSteps?: string[] }`

---

### activate_action_list_tools
Prepare action list tools with status check.

**Parameters**: None

**Returns**: `{ activated: boolean, serverStatus, availableTools: string[], toolDescriptions, nextSteps?: string[] }`

---

## Error Semantics (Utilities)

From `src/core/errors.ts`:
- `AppError` base; retryability determined by `isRetryableError(err)`
- Common errors: `BackendUnavailableError`, `BackendTimeoutError`, `ValidationError`, `ConflictError`, `NotFoundError`, `TimeoutError`, `CircuitBreakerOpenError`, `InternalError`

Handling guidance:
- Retry transient errors (`TimeoutError`, `BackendUnavailableError`) with backoff
- Do not retry `ValidationError`/`ConflictError` without correcting input or concurrency meta
- Tool-level errors return `{ isError: true, errorCode, message }` inside `structuredContent`; protocol-level errors throw/raise at call boundary.

---

## Testing Guidance

Smoke validation:
- Run VS Code task `test:smoke` to validate unit tests excluding slow markers
- Inspect `artifacts/test/smoke/pytest.log` and `results.json` for failures

Contract validation:
- Compare tool input/output against Zod schemas (`src/core/schemas.ts`)
- Ensure `structuredContent` is populated and matches expected shape
- For updates, assert conflict handling by simulating stale `concurrencyMeta` and expecting `ConflictError`.
- Verify toggle operations mutate state idempotently and return consistent item shape.

---

## Cross-References

- **Schemas**: `TaskMan-v2/mcp-server-ts/src/core/schemas.ts`
- **Types**: `TaskMan-v2/mcp-server-ts/src/core/types.ts`
- **Backend client**: `TaskMan-v2/mcp-server-ts/src/backend/client.ts`
- **Circuit breaker**: `TaskMan-v2/mcp-server-ts/src/backend/client-with-circuit-breaker.ts`
- **Feature registration**:
  - Projects: `TaskMan-v2/mcp-server-ts/src/features/projects/register.ts`
  - Tasks: `TaskMan-v2/mcp-server-ts/src/features/tasks/register.ts`
  - Action Lists: `TaskMan-v2/mcp-server-ts/src/features/action-lists/register.ts`
  - Activation: `TaskMan-v2/mcp-server-ts/src/features/activation/register.ts`
- **Config**: `TaskMan-v2/mcp-server-ts/src/config/index.ts`
- **Locking**: `TaskMan-v2/mcp-server-ts/src/infrastructure/locking.ts`
- **Audit**: `TaskMan-v2/mcp-server-ts/src/infrastructure/audit.ts`

---

## Resumable TODOs

- [x] Fill exact tool names for action lists (including toggle_item); verify others via registration files
- [x] Add parameter details/examples for core tools (projects, tasks, action_lists)
- [x] Include example payloads and expected `structuredContent` outputs
- [x] Document action_lists edge case: toggle item semantics and errors
- [x] Cross-check all names/filters against `register.ts` and `schemas.ts`
- [x] Add tables for all tools with parameter details
- [x] Document bulk operations (task_bulk_update, action_list_bulk_delete, etc.)
- [x] Document search tools (task_search, action_list_search)
- [x] Document activation tools
- [ ] Add TypeDoc links when generated
- [ ] Add integration test examples

---

## Changelog
- 2025-12-04: Initial scaffold created; ready for enrichment.
- 2025-12-04: Enriched tool index, concurrency guidance, examples (projects/sprints/tasks/action_lists), testing notes, and TODO progress.
- 2025-12-05: **Major update** - Corrected tool naming from dot notation to underscore (`entity_action`). Expanded from 21 to 40 documented tools. Added full documentation for:
  - 4 Activation tools (`activate_taskman_server`, etc.)
  - 13 Project tools (including sprint, comment, blocker, meta-task operations)
  - 10 Task tools (including bulk operations and search)
  - 13 Action List tools (including bulk operations and search)
  - Updated cross-references to correct file paths
