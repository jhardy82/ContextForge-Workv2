---
title: "Schema and Command Standardization Summary"
created: "2025-08-27"
last_updated: "2025-08-27"
last_validated: "2025-08-27"
phase: "Schema Standardization"
status: "complete"
version: "1.0"
author: "ContextForge Agent"
purpose: "Document comprehensive schema unification across Tasks, Sprints, Projects"
---

# Schema and Command Standardization Summary

## Overview
Implemented comprehensive standardization across Projects, Sprints, and Tasks to ensure consistent command interfaces, parameter naming, and validation approaches.

## Key Standardizations

### 1. Status Values (Unified)
**Before**: Each entity had different status values
- Tasks: `["new", "in_progress", "blocked", "review", "done", "dropped"]`
- Sprints: `["planned", "active", "complete", "closed"]`
- Projects: `["planned", "active", "on_hold", "complete", "closed"]`

**After**: Unified status constants with backward compatibility
- **Common Statuses**: `["planned", "active", "blocked", "review", "done", "closed"]`
- Tasks accept both new unified statuses and legacy statuses for backward compatibility
- All entities now use the same core lifecycle states

### 2. Parameter Names (Consistent)
**Before**: Inconsistent naming across entities
- Tasks used `assignees`, Projects used `owner`
- Tasks used `summary`, Sprints used `goal`, Projects had no description

**After**: Unified parameter naming
- **owner**: Consistent across all entities (maps to `assignees` in task storage for compatibility)
- **description**: Consistent description field across all entities (maps to existing storage fields)
- **status**: Same validation and values across all entities
- **priority**: Uses shared `PRIORITIES` constant for tasks (extensible to other entities)

### 3. Command Availability (Complete Parity)
**Before**: Missing commands
- Tasks: Missing `details` command
- Different command availability across entities

**After**: Complete command parity
- **All entities** now support: `list`, `show`, `create`, `update`, `delete`, `stats`, `details`
- Consistent command signatures and behaviors
- Rich console output with same formatting patterns

### 4. Validation (Standardized)
**Before**: Mixed validation approaches
- Hardcoded validation lists in some places
- Inconsistent error messages
- Different risk level validations

**After**: Unified validation constants
- **COMMON_STATUSES**: Shared across all entities
- **PRIORITIES**: Shared priority levels
- **RISK_LEVELS**: `["low", "medium", "high", "critical"]` used consistently
- Standardized error message formats

## Backward Compatibility

### Field Mapping Strategy
To maintain compatibility with existing CSV schemas:

1. **Tasks**:
   - `description` parameter → maps to `summary` field in CSV
   - `owner` parameter → maps to `assignees` field in CSV
   - Accepts both new unified and legacy status values

2. **Sprints**:
   - `description` parameter → maps to `goal` field in CSV
   - Maintains all existing field mappings

3. **Projects**:
   - `description` parameter → maps to `notes` field in CSV
   - All existing fields preserved

### Legacy Support
- **TASK_STATUSES** constant maintained for backward compatibility
- Status validation accepts both unified and legacy values for tasks
- Existing field names in CSV files unchanged
- Migration path: parameter interface standardized, storage mapping preserved

## Command Examples

### Unified Creation Syntax

```bash
# Tasks
python dbcli.py task create "Task Title" --description "Task description" --status planned --owner john.doe

# Sprints
python dbcli.py sprint create "Sprint Title" --description "Sprint description/goal" --status planned --project-id P-123

# Projects
python dbcli.py project create "Project Title" --description "Project description" --status planned --owner jane.doe
```

### Unified Update Syntax

```bash
# All entities support same parameter patterns
python dbcli.py task update T-123 --description "New description" --status active
python dbcli.py sprint update S-123 --description "New goal" --status active
python dbcli.py project update P-123 --description "New description" --status active
```

### Unified Details Commands

```bash
# All entities now support rich details view
python dbcli.py task details T-123
python dbcli.py sprint details S-123
python dbcli.py project details P-123
```

## Implementation Benefits

1. **Consistent User Experience**: Same parameter names and patterns across all entity types
2. **Reduced Cognitive Load**: Users learn one pattern, apply everywhere
3. **Maintainable Code**: Shared constants and validation logic
4. **Extensible Design**: Easy to add new entity types following same patterns
5. **Backward Compatible**: Existing workflows continue to work
6. **Rich Interface Parity**: All entities have same level of detail and formatting

## Technical Implementation

### Constants Structure

```python
# Unified status constants across all entity types
COMMON_STATUSES = ["planned", "active", "blocked", "review", "done", "closed"]
PRIORITIES = ["low", "medium", "high", "critical"]
RISK_LEVELS = ["low", "medium", "high", "critical"]

# Legacy compatibility
TASK_STATUSES = ["new", "in_progress", "blocked", "review", "done", "dropped"]
```

### Validation Pattern

```python
# Unified validation approach
if status not in COMMON_STATUSES and status not in TASK_STATUSES:
    console.print(f"[red]Invalid status. Must be one of: {', '.join(COMMON_STATUSES)}[/red]")
    raise typer.Exit(1)
```

### Field Mapping Pattern

```python
# Backward-compatible field mapping
new_task = {
    "summary": description,  # Map description to summary field
    "assignees": owner,      # Map owner to assignees field
    # ... other fields
}
```

## Migration Path

1. **Phase 1** (Current): Parameter interface standardized, backward-compatible storage
2. **Phase 2** (Future): Optional CSV schema migration to unified field names
3. **Phase 3** (Future): Deprecate legacy parameter aliases
4. **Phase 4** (Future): Full schema unification

This approach ensures smooth transition while immediately providing consistent user experience across all entity types.
