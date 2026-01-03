---
description: Authoritative CLI usage guide - which CLI tool to use for task/sprint/project operations
applyTo: "**/*task*", "**/*sprint*", "**/*project*", "**/*cf*", "**/*cli*", "**/*dbcli*"
---

---

## ⚠️ CRITICAL: Use the Modular CLI

**ALWAYS use `cf_core.cli.main` for task/sprint/project operations.**

```bash
# ✅ CORRECT - Use this modular CLI
python -m cf_core.cli.main task list
python -m cf_core.cli.main task create "My Task" --priority high
python -m cf_core.cli.main task get T-20251215-001
python -m cf_core.cli.main task update T-001 --status in_progress
python -m cf_core.cli.main sprint list
python -m cf_core.cli.main sprint create "Sprint Name" --start 2025-01-01 --end 2025-01-14

# 🤖 Machine mode (JSON output for agents)
python -m cf_core.cli.main --machine task list
python -m cf_core.cli.main --machine task get T-001
```

---

## 🚫 DEPRECATED - Do NOT Use These

```bash
# ❌ WRONG - scripts/cli/dbcli.py is DEPRECATED
python scripts/cli/dbcli.py task list    # DON'T USE
python dbcli.py task create              # DON'T USE

# ❌ WRONG - cf_cli.py is also legacy
python cf_cli.py task list               # DON'T USE
```

---

## Available Commands

### Task Commands (cf_core.cli.main task)
- `list` - List tasks with optional filters (--status, --sprint, --assignee)
- `get <id>` - Get task details by ID
- `create <title>` - Create new task (--priority, --status, --sprint, --project)
- `update <id>` - Update task (--title, --status, --priority, --sprint)
- `delete <id>` - Delete task
- `complete <id>` - Mark task complete
- `start <id>` - Start working on task (sets in_progress)
- `block <id>` - Block task with reason
- `unblock <id>` - Unblock task

### Sprint Commands (cf_core.cli.main sprint)
- `list` - List all sprints
- `get <id>` - Get sprint details
- `create <name>` - Create sprint (--start, --end required)
- `delete <id>` - Delete sprint

### Project Commands (cf_core.cli.main project)
- `list` - List all projects
- (create, get, update, delete - coming soon)

### Config Commands (cf_core.cli.main config)
- `show` - Show current configuration

---

## Machine Mode for Agents

When agents need structured output, use `--machine` flag:

```bash
python -m cf_core.cli.main --machine task list
```

This returns JSON with consistent structure:
```json
{
  "success": true,
  "data": { ... },
  "meta": { "request_id": "...", "version": "0.1.0" },
  "timestamp": "2025-12-15T..."
}
```

---

## Why This Matters

The `cf_core.cli.main` module is:
1. **Modular** - Uses Typer command groups (task_app, sprint_app, project_app)
2. **Service-backed** - Uses TaskManService with proper repository pattern
3. **Machine-friendly** - Has `--machine` mode for structured JSON output
4. **Actively maintained** - New features go here, not dbcli

The `scripts/cli/dbcli.py` is:
1. **Legacy** - Over 3600 lines of monolithic code
2. **Deprecated** - Marked for migration/removal
3. **CSV-based** - Uses different data authority model
4. **Not recommended** - May produce inconsistent results

---

## Quick Reference

| Operation | Command |
|-----------|---------|
| List all tasks | `python -m cf_core.cli.main task list` |
| Create task | `python -m cf_core.cli.main task create "Title" --priority high` |
| View task | `python -m cf_core.cli.main task get T-001` |
| Update task | `python -m cf_core.cli.main task update T-001 --status done` |
| List sprints | `python -m cf_core.cli.main sprint list` |
| Create sprint | `python -m cf_core.cli.main sprint create "Name" --start 2025-01-01 --end 2025-01-14` |
| View config | `python -m cf_core.cli.main config show` |
