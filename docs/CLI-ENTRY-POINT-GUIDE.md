# CLI Entry Point Guide

**Status**: Active
**Version**: 1.0
**Last Updated**: 2025-11-29
**Purpose**: Consolidate all `cf` CLI alias documentation for future agents

---

## Primary Entry Point: `cf`

The `cf` command is the **authoritative CLI entry point** for all ContextForge operations. It is a PowerShell alias for `cf_cli.py`.

### Quick Reference

```powershell
# Task Management
cf task list                                    # List all tasks
cf task create --title "New Task" --priority high  # Create a task
cf task show T-001                              # View task details
cf task update T-001 --status in_progress       # Update task status

# Project Management
cf project list                                 # List projects
cf project upsert --id P-001 --title "Project Name"

# Sprint Management
cf sprint list                                  # List sprints
cf sprint upsert --id S-2025-01 --project-id P-001 --title "Sprint 1"

# Status and Migration
cf status migration --json
cf context sync
```

### Fallback (if alias unavailable)

```powershell
python cf_cli.py task list
python cf_cli.py task create --title "New Task" --priority high
```

---

## Alias Definition

The `cf` alias is defined in the `ContextForge.PythonIntegration` PowerShell module:

**Location**: `modules/ContextForge.PythonIntegration/ContextForge.PythonIntegration.psm1`

```powershell
# Alias resolves to:
# python cf_cli.py <args>
```

### Verifying Alias Availability

```powershell
# Check if alias exists
Get-Alias cf

# Full verification
Get-Alias cf | Format-List
Get-Command -Module ContextForge.PythonIntegration | Select-Object -Property Name, CommandType
```

---

## Documentation Files Referencing `cf`

The following files have been updated to reference the `cf` alias:

### Core Documentation

| File | Section | Status |
|------|---------|--------|
| `README.md` | CLI Entry Point section | ✅ Updated |
| `AGENTS.md` | CRITICAL section at top | ✅ Updated |
| `.github/copilot-instructions.md` | Quick Reference | ✅ Updated |
| `.github/instructions/agent-core.instructions.md` | CF_CLI Authority | ✅ Updated |

### Instruction Files

| File | Purpose |
|------|---------|
| `QSM-task-plan-implementation.instructions.md` | Task implementation workflows |
| `QSM-Workflow.instructions.md` | Universal task management |

### Other Documentation

| File | Notes |
|------|-------|
| `docs/09-Development-Guidelines.md` | Uses `cf` in examples |
| `projects/*/` documentation | May reference legacy commands |

---

## Authority Hierarchy

```
cf (PowerShell alias) → cf_cli.py - AUTHORITATIVE ORCHESTRATION LAYER
    ↓
├─→ TaskMan-v2 (task/project/sprint management)
├─→ Database Operations (PostgreSQL/SQLite via cf_cli_database_config.py)
├─→ Workflow Orchestration (QSE, TaskMan‑v2 MCP)
├─→ MCP Server Integration (task-manager, database-mcp, etc.)
├─→ Analytics (Polars, Arrow, constitutional framework)
└─→ Configuration Management (unified settings, environment variables)
```

---

## Common Mistakes to Avoid

### ❌ Wrong Patterns

```powershell
# Don't bypass cf for task operations
python tasks_cli.py list  # ❌ Legacy, not authoritative

# Don't use dbcli for task management
python dbcli.py task list  # ❌ Wrong tool

# Don't invoke cf_cli.py with pwsh wrapper
pwsh -Command "python cf_cli.py task list"  # ❌ Unnecessary wrapper
```

### ✅ Correct Patterns

```powershell
# Use cf alias (preferred)
cf task list  # ✅

# Direct Python invocation (fallback)
python cf_cli.py task list  # ✅

# With activated venv
.\.venv\Scripts\python cf_cli.py task list  # ✅
```

---

## For Future Agents

When you encounter references to CLI commands in documentation:

1. **Always prefer `cf`** as the primary command
2. **Show `python cf_cli.py`** as fallback option
3. **Update legacy references** when you find them
4. **Use this guide** as the authoritative source

### Files That May Need Updates

Search for these patterns and update to `cf`:

```bash
# Legacy patterns to find and update
grep -r "python cf_cli.py" --include="*.md"
grep -r "CF_CLI" --include="*.md"
grep -r "cf_cli.py" --include="*.md"
```

---

## Related Documents

- [AGENTS.md](../AGENTS.md) - Agent instructions with CLI authority
- [README.md](../README.md) - Main project documentation
- [09-Development-Guidelines.md](09-Development-Guidelines.md) - Development standards
- [copilot-instructions.md](../.github/copilot-instructions.md) - Copilot integration

---

**Document Maintained By**: ContextForge Team
**Last Verified**: 2025-11-29
