# ContextForge CLI Reference

**Status**: Active
**Version**: 2.0
**Last Updated**: 2025-12-16

---

## Overview

The ContextForge CLI (`cf`) provides a unified interface for task, sprint, and project management. Designed for both human developers and AI agents, it supports:

- **Human-readable output** with colors and formatting
- **Machine mode** (`--machine`) for JSON output consumable by agents
- **Noun-verb command pattern** (`cf task create`, `cf sprint show`)

---

## Installation & Quick Start

### Installation

```bash
# Install the package (from repository root)
uv pip install -e .

# Verify installation
cf --version
```

### Primary Usage (Recommended)

```bash
# Use the cf command (installed entry point)
cf task list
cf --machine task get T-001
cf sprint show S-001
```

### Alternative: Module Invocation

```bash
# If cf is not on PATH, use module invocation
python -m cf_core.cli.main task list
python -m cf_core.cli.main --machine task get T-001
```

---

## Global Options

All commands support these global options:

| Option | Short | Description |
|--------|-------|-------------|
| `--machine` | `-m` | Enable machine mode (JSON output, no color) |
| `--output FORMAT` | `-o` | Output format: json, jsonl, table, yaml, csv |
| `--no-color` | | Disable colored output |
| `--verbose` | `-v` | Enable verbose output |
| `--quiet` | `-q` | Suppress non-essential output |
| `--version` | `-V` | Show version and exit |
| `--help` | `-h` | Show help and exit |

### Machine Mode

AI agents should always use `--machine` for structured JSON output:

```bash
cf --machine task list
# Returns JSON array of tasks

cf --machine task get T-001
# Returns single task object or error response
```

---

## Command Reference

### Config Commands

#### Show Configuration

Display the effective configuration merged from all sources.

```bash
# Show configuration (secrets redacted)
cf config show

# Show all configuration including secrets
cf config show --show-secrets

# Output as JSON for machine consumption
cf --machine config show
```

---

### Health Check

```bash
# Check database and service health
cf health
cf --machine health  # JSON output with latency, task count
```

**Output (machine mode)**:
```json
{
  "status": "healthy",
  "database": "connected",
  "task_count": 8,
  "latency_ms": 0.79,
  "checked_at": "2025-12-16T04:58:52.981707+00:00"
}
```

---

### Task Commands

#### List Tasks

```bash
# List all tasks
cf task list

# Filter by status
cf task list --status in_progress
cf task list -s done

# Filter by sprint
cf task list --sprint S-001

# Filter by assignee
cf task list --assignee "agent-1"

# Combine filters with limit
cf task list --status todo --limit 10
```

**Options**:
| Option | Short | Description |
|--------|-------|-------------|
| `--status STATUS` | `-s` | Filter by status (todo, in_progress, done, blocked) |
| `--priority PRIORITY` | `-p` | Filter by priority (low, medium, high, critical) |
| `--assignee ASSIGNEE` | `-a` | Filter by assignee |
| `--project PROJECT_ID` | | Filter by project |
| `--sprint SPRINT_ID` | | Filter by sprint |
| `--limit N` | `-n` | Maximum tasks to return (default: 50) |

---

#### Search Tasks

```bash
# Keyword search in title and description
cf task search "API endpoint"

# Search with filters
cf task search "auth" --status in_progress
cf task search "bug" --priority high
cf task search --tags "urgent,p0"

# Combined criteria
cf task search "database" --status todo --priority high --limit 5
```

**Options**:
| Option | Short | Description |
|--------|-------|-------------|
| `QUERY` | | Search term (matches title/description) |
| `--status STATUS` | `-s` | Filter by status |
| `--priority PRIORITY` | `-p` | Filter by priority |
| `--assignee ASSIGNEE` | `-a` | Filter by assignee |
| `--tags TAGS` | `-t` | Filter by tags (comma-separated) |
| `--limit N` | `-n` | Maximum results (default: 50) |

---

#### Get Task

```bash
# Get task details by ID
cf task get T-20251216-0001
cf --machine task get T-001  # JSON output
```

---

#### Create Task

```bash
# Basic task
cf task create "Implement authentication"

# With options
cf task create "Fix login bug" --priority high --status in_progress
cf task create "Write docs" --sprint S-001 --assignee "agent-1"
cf task create "Review PR" --estimate 2.0 --tags "review,urgent"
```

**Options**:
| Option | Short | Description |
|--------|-------|-------------|
| `TITLE` | | Task title (required) |
| `--description TEXT` | `-d` | Task description |
| `--status STATUS` | `-s` | Initial status (default: todo) |
| `--priority PRIORITY` | `-p` | Priority level (default: medium) |
| `--sprint SPRINT_ID` | | Assign to sprint |
| `--project PROJECT_ID` | | Assign to project |
| `--assignee ASSIGNEE` | `-a` | Assign to user/agent |
| `--estimate HOURS` | `-e` | Estimated hours |
| `--tags TAGS` | `-t` | Comma-separated tags |

---

#### Update Task

```bash
# Update status
cf task update T-001 --status in_progress

# Update multiple fields
cf task update T-001 --priority high --assignee "agent-2"

# Log hours worked
cf task update T-001 --actual-hours 2.5
```

---

#### Move Task

```bash
# Move task to a sprint
cf task move T-001 S-002

# Remove task from sprint (unassign)
cf task move T-001 none
```

---

#### Task Lifecycle Commands

```bash
# Start working on a task
cf task start T-001

# Complete a task
cf task complete T-001

# Block a task
cf task block T-001 --reason "Waiting for API access"

# Unblock a task
cf task unblock T-001
```

---

#### Delete Task

```bash
cf task delete T-001
```

---

### Sprint Commands

#### List Sprints

```bash
cf sprint list
cf --machine sprint list
```

---

#### Show Sprint (with progress)

```bash
# Show sprint with visual progress bar and tasks
cf sprint show S-001
```

**Human output**:
```
Sprint: December Sprint (S-20251215233123)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: active | 2025-12-15 → 2025-12-29

Progress: [████████████░░░░░░░░░░░░░░░░░] 37.5% (3/8 tasks)
  ✓ Done: 3  ⟳ In Progress: 2  ○ Todo: 2  ⊘ Blocked: 1

Tasks in Sprint:
 ✓ T-001  Implement search         done         high
 ⟳ T-002  Add progress bar         in_progress  medium
 ○ T-003  Write documentation      todo         low
```

---

#### Get Sprint

```bash
# Get sprint details without task visualization
cf sprint get S-001
cf --machine sprint get S-001
```

---

#### Create Sprint

```bash
cf sprint create "Sprint 5" --start 2025-01-01 --end 2025-01-14
cf sprint create "Q1 Sprint" --project P-001
```

---

#### Update Sprint

```bash
cf sprint update S-001 --status completed
cf sprint update S-001 --end 2025-01-21
```

---

#### Delete Sprint

```bash
cf sprint delete S-001
```

---

### Project Commands

#### List Projects

```bash
cf project list
cf --machine project list
```

---

#### Get Project

```bash
cf project get P-001
```

---

#### Create Project

```bash
cf project create "New Feature" --description "Implement new feature set"
```

---

#### Update Project

```bash
cf project update P-001 --status active
```

---

#### Delete Project

```bash
cf project delete P-001
```

---

## Command Distinctions

Understanding when to use each command:

| Command | Purpose | Use When |
|---------|---------|----------|
| `task get ID` | Fetch single task | You have an ID and need details |
| `task list` | List with filters | Browsing tasks by status/sprint |
| `task search QUERY` | Keyword search | Looking for specific content |
| `sprint get ID` | Basic sprint info | Just need sprint metadata |
| `sprint show ID` | Rich display | Want progress bar and task list |

---

## Machine Mode Responses

### Success Response

```json
{
  "id": "T-20251216-0001",
  "title": "Implement feature",
  "status": "in_progress",
  "priority": "high"
}
```

### Error Response

```json
{
  "success": false,
  "code": "NOT_FOUND",
  "message": "Task T-999 not found",
  "exit_code": 2
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Not found |
| 3 | Invalid argument |
| 4 | Permission denied |

---

## Examples by Use Case

### AI Agent Workflow

```bash
# List active tasks in machine mode
cf --machine task list --status in_progress

# Create and track a task
TASK_ID=$(cf --machine task create "Fix bug" | jq -r '.id')
cf task start $TASK_ID
# ... do work ...
cf task complete $TASK_ID
```

### Sprint Planning

```bash
# Create sprint
cf sprint create "Week 50" --start 2025-12-16 --end 2025-12-22

# Move tasks into sprint
cf task move T-001 S-20251216
cf task move T-002 S-20251216

# Check progress
cf sprint show S-20251216
```

### Daily Standup

```bash
# What's in progress?
cf task list --status in_progress

# What's blocked?
cf task list --status blocked

# Sprint progress
cf sprint show S-current
```

---

## Troubleshooting

### Module Not Found

```bash
# Ensure package is installed
cd /path/to/SCCMScripts
& .venv/Scripts/Activate.ps1
uv pip install -e .

# Test the cf command
cf --help
```

### Database Connection Issues

```bash
# Check health endpoint
cf health

# Verify database file exists
ls db/taskman.sqlite
```

### Invalid Status/Priority Values

Valid values:
- **Status**: `todo`, `in_progress`, `done`, `blocked`
- **Priority**: `low`, `medium`, `high`, `critical`

---

## Related Documentation

- [AGENTS.md](../AGENTS.md) - Agent instructions with CLI reference
- [09-Development-Guidelines.md](09-Development-Guidelines.md) - Development practices
- [10-API-Reference.md](10-API-Reference.md) - API documentation
- [13-Testing-Validation.md](13-Testing-Validation.md) - Testing standards

---

## Migration from Legacy CLI

**DEPRECATED - Files Removed in December 2025**: The previous `cf_cli.py`, `tasks_cli.py`, and `dbcli.py` have been removed.

All functionality is now available through the `cf` command:

| Legacy Command | New Command |
|----------------|-------------|
| `python cf_cli.py task list` | `cf task list` |
| `python cf_cli.py task show T-001` | `cf task get T-001` |
| `python tasks_cli.py list` | `cf task list` |
| `python -m cf_core.cli.main ...` | `cf ...` (if on PATH) |

**Installation Required**: If upgrading from an older version, reinstall:
```bash
uv pip install -e .
```
