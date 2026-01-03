# CLI-MCP Parity Matrix

**Status**: Active
**Version**: 1.0.0
**Created**: 2025-11-29
**Purpose**: Define feature parity between CF_CLI (Python) and TaskMan-v2 MCP (TypeScript)

---

## Overview

This document tracks the parity between:
- **CF_CLI** (`cf_cli.py`, `tasks_cli.py`) - Python command-line interface
- **TaskMan-v2 MCP** (`vs-code-task-manager/mcp-server-ts/`) - TypeScript MCP server

Per AGENTS.md: *"CF_CLI is the authoritative orchestration entry point for CF_CORE operations"* and *"Maintain feature parity between MCP surfaces and CF_CLI."*

---

## Parity Status Summary

| Domain | CLI Commands | MCP Tools | Parity Status |
|--------|-------------|-----------|---------------|
| **Tasks** | 12 commands | 10 tools | 🟡 Partial |
| **Projects** | 4 commands | 12 tools | 🔴 MCP ahead |
| **Sprints** | 7 commands | 0 tools | 🔴 CLI ahead |
| **Action Lists** | 0 commands | 12 tools | 🔴 MCP ahead |
| **Status/Config** | 15+ commands | 0 tools | 🔴 CLI ahead |
| **Velocity** | 4 commands | 0 tools | 🔴 CLI ahead |
| **Context** | 5 commands | 0 tools | 🔴 CLI ahead |

---

## Detailed Parity Analysis

### Tasks Domain

#### CLI Commands (tasks_cli.py)

| Command | Aliases | Parameters | MCP Equivalent | Status |
|---------|---------|------------|----------------|--------|
| `create` | `New-Task` | title, description, project, sprint, priority, status, type, assignee, labels, tags, story_points, actual_hours | `task_create` | ✅ Parity |
| `update` | `Set-Task` | task_id, title, description, status, priority, etc. | `task_update` | ✅ Parity |
| `show` | `Get-TaskDetail` | task_id, json | `task_read` | ✅ Parity |
| `list` | `Get-Task` | project, sprint, status, limit, offset, sort_by, sort_order | `task_list` | ✅ Parity |
| `upsert` | - | task_id + all create params | - | ❌ CLI only |
| `enhance` | - | AI enhancement | - | ❌ CLI only |
| `status-counts` | - | project, sprint | - | ❌ CLI only |
| `bulk-update` | - | filter-expr, status, priority, batch-size | `task_bulk_update` | ✅ Parity |
| `bulk-list` | - | filter-expr, limit, columns | - | ❌ CLI only |
| `diag-rich` | - | diagnostic | - | ❌ CLI only (dev) |
| `rich-mode` | - | toggle Rich UI | - | ❌ CLI only (dev) |
| `rich-demo` | - | demo Rich output | - | ❌ CLI only (dev) |

#### MCP Tools (tasks/register.ts)

| Tool | Parameters | CLI Equivalent | Status |
|------|------------|----------------|--------|
| `task_create` | taskSchema | `create` | ✅ Parity |
| `task_read` | id | `show` | ✅ Parity |
| `task_update` | id, taskUpdateSchema | `update` | ✅ Parity |
| `task_set_status` | id, status, notes, reason, notify | - | ❌ MCP only |
| `task_assign` | id, assignees, notify | - | ❌ MCP only |
| `task_delete` | id | - | ❌ MCP only |
| `task_list` | filters, pagination, sorting | `list` | ✅ Parity |
| `task_bulk_update` | ids, updates | `bulk-update` | ✅ Parity |
| `task_bulk_assign_sprint` | taskIds, sprintId | - | ❌ MCP only |
| `task_search` | query, filters | - | ❌ MCP only |

---

### Projects Domain

#### CLI Commands (cf_cli.py)

| Command | Parameters | MCP Equivalent | Status |
|---------|------------|----------------|--------|
| `project upsert` | id, title, status, metadata | `project_create`/`project_update` | ✅ Parity |
| `project show` | project_id | `project_read` | ✅ Parity |
| `project list` | filters | `project_list` | ✅ Parity |
| `project tasks` | project_id | - | ❌ CLI only |

#### MCP Tools (projects/register.ts)

| Tool | Parameters | CLI Equivalent | Status |
|------|------------|----------------|--------|
| `project_create` | projectSchema | `upsert` | ✅ Parity |
| `project_read` | id | `show` | ✅ Parity |
| `project_update` | id, updates | `upsert` | ✅ Parity |
| `project_delete` | id | - | ❌ MCP only |
| `project_list` | filters | `list` | ✅ Parity |
| `project_add_sprint` | projectId, sprintId | - | ❌ MCP only |
| `project_remove_sprint` | projectId, sprintId | - | ❌ MCP only |
| `project_add_meta_task` | projectId, title, type, priority | - | ❌ MCP only |
| `project_add_comment` | projectId, content, author | - | ❌ MCP only |
| `project_add_blocker` | projectId, description, severity | - | ❌ MCP only |
| `project_get_comments` | projectId | - | ❌ MCP only |
| `project_get_metrics` | projectId | - | ❌ MCP only |

---

### Sprints Domain

#### CLI Commands (cf_cli.py)

| Command | Parameters | MCP Equivalent | Status |
|---------|------------|----------------|--------|
| `sprint create` | title, project, start_date, end_date | - | ❌ CLI only |
| `sprint list` | project, status | - | ❌ CLI only |
| `sprint show` | sprint_id | - | ❌ CLI only |
| `sprint update` | sprint_id, title, status | - | ❌ CLI only |
| `sprint status` | sprint_id | - | ❌ CLI only |
| `sprint normalize` | sprint_id | - | ❌ CLI only |
| `sprint upsert` | id, title, project, dates | - | ❌ CLI only |

#### MCP Tools

**⚠️ CRITICAL GAP: No Sprint MCP tools exist yet!**

The REST API exists at `/api/v1/sprints/*` but MCP tool wrappers are missing.

**Required Sprint MCP Tools** (to be created):
- `sprint_create` - Create a new sprint
- `sprint_read` - Get sprint by ID
- `sprint_update` - Update sprint
- `sprint_delete` - Delete sprint
- `sprint_list` - List sprints with filters
- `sprint_add_task` - Add task to sprint
- `sprint_remove_task` - Remove task from sprint
- `sprint_get_metrics` - Get sprint velocity/burndown

---

### Action Lists Domain

#### CLI Commands

**No CLI commands exist for Action Lists.**

#### MCP Tools (action-lists/register.ts)

| Tool | Parameters | CLI Equivalent | Status |
|------|------------|----------------|--------|
| `action_list_create` | title, description, category, sprintId | - | ❌ MCP only |
| `action_list_read` | id | - | ❌ MCP only |
| `action_list_list` | filters | - | ❌ MCP only |
| `action_list_update` | id, updates | - | ❌ MCP only |
| `action_list_delete` | id | - | ❌ MCP only |
| `action_list_add_item` | listId, content, order | - | ❌ MCP only |
| `action_list_toggle_item` | listId, itemId | - | ❌ MCP only |
| `action_list_remove_item` | listId, itemId | - | ❌ MCP only |
| `action_list_reorder_items` | listId, itemIds | - | ❌ MCP only |
| `action_list_bulk_delete` | ids | - | ❌ MCP only |
| `action_list_bulk_update` | ids, updates | - | ❌ MCP only |
| `action_list_search` | query, filters | - | ❌ MCP only |

---

### Status/Config Domain (CLI Only)

These commands are CLI-specific for system administration:

| Command Group | Commands | Purpose |
|---------------|----------|---------|
| `status` | migration, database-authority, production-optimization, error-recovery, libraries, repair, query, validate, parse-error-scan, duckdb, hours-scan | System diagnostics |
| `config` | show, dump-env, benchmark-startup, benchmark-cold-startup, performance-stats, clear-cache | Configuration management |
| `ontology` | create-snapshot, show | COF/UCL ontology tracking |
| `drift` | monitor, check | Configuration drift detection |
| `benchmark` | libraries | Library performance testing |
| `plugins` | list | Plugin management |

---

### Velocity Domain (CLI Only)

| Command | Parameters | Purpose |
|---------|------------|---------|
| `velocity record` | task_id, hours, story_points | Record velocity data |
| `velocity report` | sprint, project, format | Generate velocity reports |
| `velocity predict` | sprint, project | Predict completion |
| `velocity show` | sprint, project | Display velocity metrics |

---

## Priority Remediation Roadmap

### Phase 1: Sprint MCP Tools (HIGH PRIORITY)

**Gap**: Sprints have 7 CLI commands but 0 MCP tools.

**Action**: Create `vs-code-task-manager/mcp-server-ts/src/features/sprints/` with:
1. `register.ts` - Tool definitions
2. `schemas.ts` - Zod validation schemas
3. `handlers.ts` - API client calls

**Estimated Effort**: 3-5 story points

---

### Phase 2: CLI Enhancements to Match MCP

**MCP-only features to add to CLI**:

| Feature | MCP Tool | CLI Command to Add |
|---------|----------|-------------------|
| Task deletion | `task_delete` | `tasks delete <id>` |
| Task search | `task_search` | `tasks search <query>` |
| Task assignment | `task_assign` | `tasks assign <id> --assignees` |
| Status with notes | `task_set_status` | `tasks set-status <id> --notes` |
| Project deletion | `project_delete` | `project delete <id>` |
| Project comments | `project_add_comment` | `project comment <id>` |
| Project blockers | `project_add_blocker` | `project blocker <id>` |
| Project metrics | `project_get_metrics` | `project metrics <id>` |

**Estimated Effort**: 8-13 story points

---

### Phase 3: Action Lists CLI

**Gap**: 12 MCP tools, 0 CLI commands.

**Action**: Create `actions_cli.py` with:
- `action-list create/show/list/update/delete`
- `action-list add-item/toggle-item/remove-item`
- `action-list bulk-update/bulk-delete`

**Estimated Effort**: 5-8 story points

---

### Phase 4: MCP Status/Config Tools (Optional)

Consider adding MCP tools for:
- `status_check` - System health
- `config_get` - Configuration values
- `velocity_record` - Velocity tracking

**Estimated Effort**: 3-5 story points

---

## Parity Enforcement Strategy

### CI/CD Validation

```yaml
# .github/workflows/parity-check.yml
- name: Validate CLI-MCP Parity
  run: |
    python scripts/validate_parity.py \
      --cli-commands cf_cli.py,tasks_cli.py \
      --mcp-tools vs-code-task-manager/mcp-server-ts/src/features/*/register.ts \
      --matrix docs/CLI-MCP-PARITY-MATRIX.md
```

### Manual Review Cadence

- **Weekly**: Check for new CLI commands without MCP equivalents
- **Sprint**: Update parity matrix with new features
- **Release**: Full parity audit before major releases

---

## Related Documents

- [AGENTS.md](../AGENTS.md) - CF_CLI authority and MCP transport policy
- [docs/15-Future-Roadmap.md](15-Future-Roadmap.md) - MCP integration roadmap
- [TaskMan-v2/README.md](../TaskMan-v2/README.md) - MCP server documentation

---

**Document Maintainer**: ContextForge Architecture Team  
**Last Updated**: 2025-11-29
