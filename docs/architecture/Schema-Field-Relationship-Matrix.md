# Schema Field Relationship Matrix

> **Version**: 1.2.0
> **Last Updated**: 2025-12-28
> **Status**: Active

This document describes the field relationships across ContextForge tracker entities (Task, Sprint, Project) as revealed through Sacred Geometry analysis and Spatial Reasoning.

## Sacred Geometry Patterns

### Trinity (3-fold) - Entity Identification

All entities share a consistent identification pattern using prefixed IDs:

| Entity | ID Pattern | Regex | Example |
|--------|-----------|-------|---------|
| Task | `T-{suffix}` | `^T-[A-Za-z0-9_-]+$` | `T-001`, `T-feature-auth` |
| Sprint | `S-{suffix}` | `^S-[A-Za-z0-9_-]+$` | `S-2025-Q1`, `S-sprint-42` |
| Project | `P-{suffix}` | `^P-[A-Za-z0-9_-]+$` | `P-CORE`, `P-contextforge` |

### Quadrant (4-fold) - Temporal Fields

All entities share a temporal lifecycle pattern:

```
created_at → start_date → end_date → completed_at
    │            │           │            │
    v            v           v            v
 Genesis      Begin       Target       Actual
```

| Field | Task | Sprint | Project | Purpose |
|-------|------|--------|---------|---------|
| `created_at` | Yes | Yes | Implicit | Record creation timestamp |
| `start_date` | Implicit | Yes | Yes | Work begins |
| `end_date` | `due_at` | Yes | `target_end_date` | Target completion |
| `completed_at` | Yes | Yes | Yes | Actual completion timestamp |

### Pentagon (5-fold) - Status Lifecycle

Unified status values across all entities (v1.2.0):

```
                    new
                   /   \
                  v     v
           pending ←→ assigned
                |       |
                v       v
              active ←→ in_progress
                |       |
                v       v
           blocked ←→ completed
                |
                v
            cancelled
```

| Status | Task | Sprint | Project | Description |
|--------|------|--------|---------|-------------|
| `new` | Yes | Yes | Yes | Newly created, not yet started |
| `pending` | Yes | Yes | Yes | Awaiting external input (requires `pending_reason`) |
| `assigned` | No | Yes | Yes | Assigned to owner/team |
| `active` | No | Yes | Yes | Work has begun |
| `in_progress` | Yes | Yes | Yes | Work is actively being done |
| `blocked` | Yes | Yes | Yes | Work is blocked (requires `blocked_reason`) |
| `completed` | Yes | Yes | Yes | Work is done (requires `completed_at`) |
| `cancelled` | Yes | Yes | Yes | Work was abandoned |

**Note**: Task uses a slightly different status set: `new`, `ready`, `in_progress`, `blocked`, `review`, `done`, `dropped`

### Hexad (6-fold) - Coupled Field Pairs

Status values couple with specific fields:

| Status | Required Field | Type | Description |
|--------|---------------|------|-------------|
| `pending` | `pending_reason` | `string` | Why entity is on hold |
| `blocked` | `blocked_reason` | `string` | What is blocking progress |
| `completed` | `completed_at` | `datetime` | When work was completed |

These couplings are enforced via Pydantic v2 model validators:

```python
@model_validator(mode="after")
def validate_completed_at(self) -> Entity:
    if self.status == "completed":
        if self.completed_at is None:
            raise ValueError("completed_at required when status is 'completed'")
    elif self.completed_at is not None:
        raise ValueError("completed_at can only be set when status is 'completed'")
    return self
```

## Cross-Entity Relationships

### Project → Sprint → Task Hierarchy

```
Project (P-xxx)
    │
    ├── Sprint (S-xxx)
    │       │
    │       ├── Task (T-xxx)
    │       ├── Task (T-xxx)
    │       └── Task (T-xxx)
    │
    └── Sprint (S-xxx)
            │
            ├── Task (T-xxx)
            └── Task (T-xxx)
```

### Association Fields

| Entity | Field | Target | Cardinality |
|--------|-------|--------|-------------|
| Task | `primary_project` | Project | Many-to-One |
| Task | `primary_sprint` | Sprint | Many-to-One |
| Task | `related_projects` | Project | Many-to-Many |
| Task | `related_sprints` | Sprint | Many-to-Many |
| Sprint | `primary_project` | Project | Many-to-One |
| Sprint | `tasks` / `task_ids` | Task | One-to-Many |
| Sprint | `related_projects` | Project | Many-to-Many |
| Project | `sprints` | Sprint | One-to-Many |
| Project | `related_projects` | Project | Many-to-Many |

## Observability Pattern

All entities share an observability structure:

```json
{
  "observability": {
    "last_health": "green|yellow|red",
    "last_heartbeat_utc": "2025-12-28T12:00:00Z",
    "evidence_log": ["log entry 1", "log entry 2"]
  }
}
```

| Health | Meaning |
|--------|---------|
| `green` | Entity is healthy, on track |
| `yellow` | Entity needs attention, minor issues |
| `red` | Entity is at risk, requires immediate action |

## Risk Entry Patterns

### Simple Risk (Task, Sprint)

```json
{
  "description": "What could go wrong",
  "impact": "low|med|high",
  "likelihood": "low|med|high",
  "mitigation": "How to prevent/address"
}
```

### Extended Risk (Project)

```json
{
  "id": "RISK-001",
  "description": "What could go wrong",
  "impact": "low|med|high",
  "likelihood": "low|med|high",
  "owner": "risk-owner@example.com",
  "mitigation": "How to prevent/address"
}
```

## Schema Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-08-01 | Initial schema |
| 1.1.0 | 2025-09-15 | Added geometry/classification fields |
| 1.1.1 | 2025-10-20 | Added computed telemetry fields |
| 1.2.0 | 2025-12-28 | Unified status lifecycle, added `completed_at`, `pending_reason`, `blocked_reason` across all entities |

## Backward Compatibility

All v1.2.0 schemas are backward compatible with:
- v1.0.0
- v1.0.1
- v1.1.0
- v1.1.1

New fields are optional, allowing gradual migration.

## State Transitions

### Sprint State Machine

Valid transitions (enforced by `can_transition_to()` method):

| From | Allowed Transitions |
|------|-------------------|
| `new` | `pending`, `assigned`, `active`, `cancelled` |
| `pending` | `active`, `cancelled` |
| `assigned` | `active`, `pending`, `cancelled` |
| `active` | `in_progress`, `blocked`, `completed`, `cancelled` |
| `in_progress` | `active`, `blocked`, `completed`, `cancelled` |
| `blocked` | `active`, `in_progress`, `cancelled` |
| `completed` | *(terminal state)* |
| `cancelled` | *(terminal state)* |

## Related Documentation

- [02-Architecture.md](../02-Architecture.md) - System architecture overview
- [05-Database-Design-Implementation.md](../05-Database-Design-Implementation.md) - Database layer details
- [Schema files](../../schemas/) - JSON Schema definitions
