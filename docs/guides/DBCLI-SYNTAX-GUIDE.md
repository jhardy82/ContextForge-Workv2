# DBCLI Complete Syntax Guide

**Version**: Production-ready (v1.0)
**Tool**: `dbcli.py` - Unified Database CLI for ContextForge Tracker System
**Last Updated**: August 28, 2025
**Target Users**: Orchestrators, automation agents, interactive users

This guide provides complete syntax documentation for the `dbcli.py` command-line interface, including all sub-applications, commands, options, and usage patterns. It is fully self-contained for orchestrator reference.

---

## 📖 Table of Contents

1. [Quick Reference](#quick-reference)
2. [Basic Usage](#basic-usage)
3. [Global Options](#global-options)
4. [Task Operations](#task-operations)
5. [Project Operations](#project-operations)
6. [Sprint Operations](#sprint-operations)
7. [Export Utilities](#export-utilities)
8. [Workflow Automation](#workflow-automation)
9. [Status & Migration](#status--migration)
10. [Active Context Management](#active-context-management)
11. [Duplicate Detection](#duplicate-detection)
12. [Utility Commands](#utility-commands)
13. [Output Formats](#output-formats)
14. [Best Practices](#best-practices)
15. [Common Patterns](#common-patterns)
16. [Error Handling](#error-handling)
17. [Troubleshooting](#troubleshooting)

---

## Quick Reference

### Basic Command Structure

```powershell
python dbcli.py [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [ARGS]
```

### Available Sub-Applications

| Sub-App | Purpose | Key Commands |
|---------|---------|--------------|
| `tasks` | Task management and CRUD operations | list, create, update, show, delete |
| `projects` | Project management and tracking | list, create, update, show, complete |
| `sprints` | Sprint planning and management | list, create, update, show, complete |
| `export` | Data export utilities | tasks, projects, sprints |
| `workflow` | Automation and bulk operations | init, status, rule, bulk-update |
| `status` | Migration and authority status | migration |
| `active` | Active context management | set, show |
| `dups` | Duplicate detection | scan, resolve |

### Most Common Commands

```powershell
# List all tasks
python dbcli.py tasks list

# Create a new task
python dbcli.py tasks create --title "New Task" --status new

# Update task status
python dbcli.py tasks update TASK-ID --status in_progress

# Export data as JSON
python dbcli.py export tasks --format json

# Check system status
python dbcli.py status migration
```

---

## Basic Usage

### Installation Requirements

- Python 3.11+
- Required packages: `typer`, `rich`, `click` (compatibility layer)
- Optional: Database backend for advanced features

### Direct Invocation

The tool is designed for direct Python invocation following ContextForge methodology:

```powershell
# Standard invocation
python dbcli.py [options] command [args]

# With virtual environment (recommended)
.venv/Scripts/python.exe dbcli.py [options] command [args]
```

### Help System

```powershell
# Main help
python dbcli.py --help

# Sub-command help
python dbcli.py tasks --help
python dbcli.py projects --help

# Specific command help
python dbcli.py tasks create --help
```

---

## Global Options

Global options apply to all commands and must be specified before the sub-command.

```powershell
python dbcli.py [GLOBAL_OPTIONS] command [args...]
```

### Available Global Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--csv-root PATH` | Path | `trackers/csv` | CSV data directory path |
| `--log-level LEVEL` | String | `INFO` | Logging level (DEBUG, INFO, WARN, ERROR) |
| `--log-path PATH` | Path | `logs/dbcli/session.log` | Custom log file path |
| `--rich-output/--no-rich-output` | Boolean | `true` | Enable/disable rich console formatting |
| `--verify/--no-verify` | Boolean | `true` | Enable/disable verification |
| `--agent-id TEXT` | String | Auto-generated | Agent identity for multi-agent coordination |

### Global Options Examples

```powershell
# Use custom CSV directory
python dbcli.py --csv-root C:/path/to/csv tasks list

# Disable rich formatting for machine processing
python dbcli.py --no-rich-output tasks list --format json

# Set specific agent ID for coordination
python dbcli.py --agent-id ORCHESTRATOR-001 tasks create --title "Test"

# Enable debug logging
python dbcli.py --log-level DEBUG tasks show TASK-001

# Custom log location
python dbcli.py --log-path C:/temp/dbcli.log tasks list
```

---

## Task Operations

Sub-command: `tasks`

The tasks sub-application provides comprehensive task management capabilities including CRUD operations, filtering, and bulk operations.

### List Tasks

```powershell
python dbcli.py tasks list [OPTIONS]
```

**Available Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--status TEXT` | String | All | Filter by status (new, in_progress, review, done, blocked, dropped) |
| `--priority TEXT` | String | All | Filter by priority (low, medium, high, critical) |
| `--project TEXT` | String | All | Filter by project ID |
| `--sprint TEXT` | String | All | Filter by sprint ID |
| `--assignee TEXT` | String | All | Filter by assignee |
| `--limit INTEGER` | Number | 100 | Maximum number of results |
| `--format TEXT` | String | table | Output format (table, json, csv) |
| `--sort-by TEXT` | String | id | Sort field (id, title, status, priority, updated_at) |
| `--reverse/--no-reverse` | Boolean | false | Reverse sort order |

**Examples:**

```powershell
# List all tasks (default table format)
python dbcli.py tasks list

# List tasks with JSON output for machine processing
python dbcli.py tasks list --format json

# Filter by status and project
python dbcli.py tasks list --status in_progress --project P-001

# List high priority tasks with limit
python dbcli.py tasks list --priority high --limit 20

# Sort by update date (newest first)
python dbcli.py tasks list --sort-by updated_at --reverse

# Multiple filters with CSV output
python dbcli.py tasks list --status new --priority high --assignee john.doe --format csv
```

### Show Task Details

```powershell
python dbcli.py tasks show TASK_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format TEXT` | String | table | Output format (table, json) |

**Examples:**

```powershell
# Show task in rich table format
python dbcli.py tasks show T-20250828-001

# Show task as JSON for processing
python dbcli.py tasks show T-20250828-001 --format json
```

### Create Task

```powershell
python dbcli.py tasks create [OPTIONS]
```

**Required Options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--title TEXT` | String | Yes | Task title |

**Optional Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--description TEXT` | String | Empty | Task description |
| `--status TEXT` | String | new | Initial status |
| `--priority TEXT` | String | medium | Priority level |
| `--project TEXT` | String | None | Associated project ID |
| `--sprint TEXT` | String | None | Associated sprint ID |
| `--assignee TEXT` | String | None | Task assignee |
| `--estimated-hours FLOAT` | Number | 0.0 | Estimated hours |
| `--tags TEXT` | String | Empty | Comma-separated tags |

**Status Values:** `new`, `in_progress`, `review`, `done`, `blocked`, `dropped`

**Priority Values:** `low`, `medium`, `high`, `critical`

**Examples:**

```powershell
# Basic task creation
python dbcli.py tasks create --title "Implement new feature"

# Full task creation with all options
python dbcli.py tasks create `
  --title "Fix authentication bug" `
  --description "Users cannot log in with SAML provider" `
  --status new `
  --priority high `
  --project P-001 `
  --sprint S-2025-08-28 `
  --assignee "john.doe" `
  --estimated-hours 4.0 `
  --tags "bug,security,urgent"

# Task with minimal required information
python dbcli.py tasks create `
  --title "Review documentation" `
  --priority low `
  --estimated-hours 1.5
```

### Update Task

```powershell
python dbcli.py tasks update TASK_ID [OPTIONS]
```

**All options are optional for updates:**

| Option | Type | Description |
|--------|------|-------------|
| `--title TEXT` | String | Update task title |
| `--description TEXT` | String | Update task description |
| `--status TEXT` | String | Update status |
| `--priority TEXT` | String | Update priority |
| `--project TEXT` | String | Update project association |
| `--sprint TEXT` | String | Update sprint association |
| `--assignee TEXT` | String | Update assignee |
| `--estimated-hours FLOAT` | Number | Update estimated hours |
| `--actual-hours FLOAT` | Number | Update actual hours worked |
| `--tags TEXT` | String | Update tags (comma-separated) |
| `--progress INTEGER` | Number | Update progress percentage (0-100) |

**Examples:**

```powershell
# Update task status
python dbcli.py tasks update T-20250828-001 --status in_progress

# Update multiple fields
python dbcli.py tasks update T-20250828-001 `
  --status review `
  --actual-hours 3.5 `
  --progress 90

# Change assignment and priority
python dbcli.py tasks update T-20250828-001 `
  --assignee "jane.smith" `
  --priority high

# Update project and sprint association
python dbcli.py tasks update T-20250828-001 `
  --project P-002 `
  --sprint S-2025-09-01
```

### Upsert Task (Create or Update)

```powershell
python dbcli.py tasks upsert [OPTIONS]
```

**Required Options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--id TEXT` | String | Yes | Explicit task ID |
| `--title TEXT` | String | Yes | Task title |

**Optional Options:** (same as create command)

**Examples:**

```powershell
# Upsert with custom ID
python dbcli.py tasks upsert `
  --id T-CUSTOM-001 `
  --title "Custom task with specific ID" `
  --status new

# Upsert existing task (will update)
python dbcli.py tasks upsert `
  --id T-20250828-001 `
  --title "Updated title" `
  --status done
```

### Delete Task

```powershell
python dbcli.py tasks delete TASK_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--force/--no-force` | Boolean | false | Skip confirmation prompt |

**Examples:**

```powershell
# Delete with confirmation prompt
python dbcli.py tasks delete T-20250828-001

# Force delete without confirmation
python dbcli.py tasks delete T-20250828-001 --force
```

### Task Statistics

```powershell
python dbcli.py tasks stats [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format TEXT` | String | table | Output format (table, json) |
| `--project TEXT` | String | All | Filter by project |
| `--sprint TEXT` | String | All | Filter by sprint |

**Examples:**

```powershell
# Overall task statistics
python dbcli.py tasks stats

# Statistics for specific project
python dbcli.py tasks stats --project P-001

# Statistics as JSON
python dbcli.py tasks stats --format json
```

### Additional Task Commands

```powershell
# Show detailed task information with relationships
python dbcli.py tasks details TASK_ID

# Import tasks from file
python dbcli.py tasks import --file tasks.csv --format csv

# Export tasks to CSV
python dbcli.py tasks export-csv --output tasks_backup.csv

# Backfill missing agent IDs
python dbcli.py tasks backfill-agent-id
```

---

## Project Operations

Sub-command: `projects`

The projects sub-application manages project lifecycle, relationships, and analytics.

### List Projects

```powershell
python dbcli.py projects list [OPTIONS]
```

**Available Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--status TEXT` | String | All | Filter by status (discovery, active, paused, closed) |
| `--owner TEXT` | String | All | Filter by project owner |
| `--limit INTEGER` | Number | 50 | Maximum number of results |
| `--format TEXT` | String | table | Output format (table, json, csv) |
| `--sort-by TEXT` | String | id | Sort field |
| `--reverse/--no-reverse` | Boolean | false | Reverse sort order |

**Status Values:** `discovery`, `active`, `paused`, `closed`

**Examples:**

```powershell
# List all projects
python dbcli.py projects list

# List active projects as JSON
python dbcli.py projects list --status active --format json

# List projects by owner
python dbcli.py projects list --owner "john.doe"

# List with custom limit and sorting
python dbcli.py projects list --limit 20 --sort-by name --reverse
```

### Show Project Details

```powershell
python dbcli.py projects show PROJECT_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format TEXT` | String | table | Output format (table, json) |

**Examples:**

```powershell
# Show project in table format
python dbcli.py projects show P-001

# Show project as JSON
python dbcli.py projects show P-001 --format json
```

### Create Project

```powershell
python dbcli.py projects create [OPTIONS]
```

**Required Options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--name TEXT` or `--title TEXT` | String | Yes | Project name |

**Optional Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--description TEXT` | String | Empty | Project description |
| `--status TEXT` | String | discovery | Initial status |
| `--owner TEXT` | String | None | Project owner |
| `--start-date TEXT` | String | None | Start date (YYYY-MM-DD) |
| `--end-date TEXT` | String | None | Target end date (YYYY-MM-DD) |
| `--priority TEXT` | String | medium | Priority level |
| `--budget FLOAT` | Number | 0.0 | Project budget |
| `--tags TEXT` | String | Empty | Comma-separated tags |

**Examples:**

```powershell
# Basic project creation
python dbcli.py projects create --name "Website Redesign"

# Comprehensive project creation
python dbcli.py projects create `
  --name "Website Redesign" `
  --description "Complete overhaul of company website" `
  --status active `
  --owner "product.manager" `
  --start-date "2025-09-01" `
  --end-date "2025-12-31" `
  --priority high `
  --budget 50000.00 `
  --tags "web,ui,customer-facing"
```

### Update Project

```powershell
python dbcli.py projects update PROJECT_ID [OPTIONS]
```

**Options:** (same as create, all optional)

**Examples:**

```powershell
# Update project status
python dbcli.py projects update P-001 --status active

# Update multiple fields
python dbcli.py projects update P-001 `
  --status paused `
  --end-date "2026-01-15" `
  --budget 75000.00

# Change owner and priority
python dbcli.py projects update P-001 `
  --owner "new.manager" `
  --priority critical
```

### Project Lifecycle Commands

```powershell
# Mark project as completed
python dbcli.py projects complete PROJECT_ID

# Upsert project (create or update by ID)
python dbcli.py projects upsert --id P-CUSTOM --name "Custom Project"

# Delete project
python dbcli.py projects delete PROJECT_ID [--force]

# Project statistics
python dbcli.py projects stats [--format json]

# Detailed project view with relationships
python dbcli.py projects details PROJECT_ID

# Import/export projects
python dbcli.py projects import --file projects.csv --format csv
python dbcli.py projects export-csv --output projects_backup.csv
```

---

## Sprint Operations

Sub-command: `sprints`

The sprints sub-application handles sprint planning, execution, and retrospectives.

### List Sprints

```powershell
python dbcli.py sprints list [OPTIONS]
```

**Available Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--status TEXT` | String | All | Filter by status (planning, active, completed, cancelled) |
| `--project TEXT` | String | All | Filter by project ID |
| `--limit INTEGER` | Number | 50 | Maximum number of results |
| `--format TEXT` | String | table | Output format (table, json, csv) |
| `--sort-by TEXT` | String | id | Sort field |
| `--reverse/--no-reverse` | Boolean | false | Reverse sort order |

**Status Values:** `planning`, `active`, `completed`, `cancelled`

**Examples:**

```powershell
# List all sprints
python dbcli.py sprints list

# List active sprints for project
python dbcli.py sprints list --status active --project P-001

# Export sprints as JSON
python dbcli.py sprints list --format json

# List recent sprints (by date)
python dbcli.py sprints list --sort-by start_date --reverse --limit 10
```

### Create Sprint

```powershell
python dbcli.py sprints create [OPTIONS]
```

**Required Options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--name TEXT` or `--title TEXT` | String | Yes | Sprint name |

**Optional Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--description TEXT` | String | Empty | Sprint description |
| `--project TEXT` | String | None | Associated project ID |
| `--start-date TEXT` | String | None | Start date (YYYY-MM-DD) |
| `--end-date TEXT` | String | None | End date (YYYY-MM-DD) |
| `--capacity FLOAT` | Number | 0.0 | Sprint capacity (hours) |
| `--goal TEXT` | String | Empty | Sprint goal |
| `--status TEXT` | String | planning | Initial status |

**Examples:**

```powershell
# Basic sprint creation
python dbcli.py sprints create --name "Sprint 2025-W35"

# Full sprint creation
python dbcli.py sprints create `
  --name "Sprint 2025-W35" `
  --description "Authentication and security features" `
  --project P-001 `
  --start-date "2025-08-25" `
  --end-date "2025-09-05" `
  --capacity 80.0 `
  --goal "Complete user authentication system" `
  --status planning

# Quick sprint with project association
python dbcli.py sprints create `
  --name "Bug Fix Sprint" `
  --project P-001 `
  --capacity 40.0 `
  --status active
```

### Sprint Management Commands

```powershell
# Update sprint
python dbcli.py sprints update SPRINT_ID [OPTIONS]

# Show sprint details
python dbcli.py sprints show SPRINT_ID [--format json]

# Mark sprint complete
python dbcli.py sprints complete SPRINT_ID

# Sprint statistics
python dbcli.py sprints stats [--project PROJECT_ID] [--format json]

# Detailed sprint view with tasks
python dbcli.py sprints details SPRINT_ID

# Sprint lifecycle
python dbcli.py sprints upsert --id S-CUSTOM --name "Custom Sprint"
python dbcli.py sprints delete SPRINT_ID [--force]

# Import/export sprints
python dbcli.py sprints import --file sprints.csv --format csv
python dbcli.py sprints export-csv --output sprints_backup.csv
```

---

## Export Utilities

Sub-command: `export`

The export sub-application provides machine-friendly data export capabilities.

### Export Tasks

```powershell
python dbcli.py export tasks [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format TEXT` | String | jsonl | Export format (jsonl, json) |
| `--output PATH` | Path | Auto-generated | Output file path |
| `--enforce/--no-enforce` | Boolean | false | Enforce post-sentinel CSV edit blocking |

**Examples:**

```powershell
# Export tasks as JSONL (default)
python dbcli.py export tasks

# Export tasks as JSON to specific file
python dbcli.py export tasks --format json --output tasks_export.json

# Export with enforcement checks
python dbcli.py export tasks --enforce

# Auto-timestamped export
python dbcli.py export tasks --format json --output "tasks_$(date +%Y%m%d).json"
```

### Export Projects and Sprints

```powershell
# Export projects
python dbcli.py export projects [OPTIONS]

# Export sprints
python dbcli.py export sprints [OPTIONS]
```

**Options are identical to export tasks**

**Examples:**

```powershell
# Export all entity types
python dbcli.py export projects --format json --output projects.json
python dbcli.py export sprints --format json --output sprints.json
python dbcli.py export tasks --format json --output tasks.json

# JSONL exports for streaming
python dbcli.py export projects --format jsonl
python dbcli.py export sprints --format jsonl
```

---

## Workflow Automation

Sub-command: `workflow`

The workflow sub-application provides automation capabilities including rule-based updates and bulk operations.

### Initialize Workflow System

```powershell
python dbcli.py workflow init [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--db-path TEXT` | String | db/workflow.sqlite | Database path |
| `--force/--no-force` | Boolean | false | Force re-initialization |

**Examples:**

```powershell
# Initialize workflow system
python dbcli.py workflow init

# Force re-initialize with custom path
python dbcli.py workflow init --db-path custom/workflow.db --force
```

### Workflow Status

```powershell
python dbcli.py workflow status [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format TEXT` | String | table | Output format (table, json) |

**Examples:**

```powershell
# Show workflow status
python dbcli.py workflow status

# Get status as JSON for monitoring
python dbcli.py workflow status --format json
```

### Create Workflow Rule

```powershell
python dbcli.py workflow rule [OPTIONS]
```

**Required Options:**

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--name TEXT` | String | Yes | Rule name |
| `--condition TEXT` | String | Yes | Trigger condition |
| `--action TEXT` | String | Yes | Action to take |

**Optional Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--enabled/--disabled` | Boolean | true | Enable rule |

**Examples:**

```powershell
# Auto-assignment rule
python dbcli.py workflow rule `
  --name "Auto-assign high priority" `
  --condition "priority=high AND assignee=null" `
  --action "assign=default.owner"

# Status transition rule
python dbcli.py workflow rule `
  --name "Auto-review ready" `
  --condition "progress>=90 AND status=in_progress" `
  --action "status=review"

# Project escalation rule
python dbcli.py workflow rule `
  --name "Overdue task escalation" `
  --condition "due_date<today AND status!=done" `
  --action "priority=high,notify=manager" `
  --enabled
```

### Bulk Operations

```powershell
python dbcli.py workflow bulk-update [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--entity TEXT` | String | task | Entity type (task, project, sprint) |
| `--filter TEXT` | String | None | Filter criteria |
| `--set TEXT` | String | None | Fields to update |
| `--dry-run/--execute` | Boolean | dry-run | Preview or execute changes |

**Examples:**

```powershell
# Preview bulk status update
python dbcli.py workflow bulk-update `
  --entity task `
  --filter "priority=low AND status=new" `
  --set "status=backlog" `
  --dry-run

# Execute bulk assignment
python dbcli.py workflow bulk-update `
  --entity task `
  --filter "project=P-001 AND assignee=null" `
  --set "assignee=team.lead" `
  --execute

# Bulk project updates
python dbcli.py workflow bulk-update `
  --entity project `
  --filter "status=discovery AND created<2025-01-01" `
  --set "status=paused" `
  --execute
```

---

## Status & Migration

Sub-command: `status`

The status sub-application provides system health and migration status information.

### Migration Status

```powershell
python dbcli.py status migration [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format TEXT` | String | table | Output format (table, json) |

**Examples:**

```powershell
# Check migration status (human-readable)
python dbcli.py status migration

# Get migration status as JSON for automation
python dbcli.py status migration --format json
```

**Sample JSON Output:**

```json
{
  "authority": "csv",
  "sentinel_present": true,
  "migration_complete": true,
  "last_migration": "2025-08-28T10:30:00Z",
  "csv_authority": true,
  "database_status": "healthy"
}
```

---

## Active Context Management

Sub-command: `active`

The active context system manages current working project and sprint context for automation workflows.

### Set Active Context

```powershell
python dbcli.py active set [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project TEXT` | String | None | Set active project ID |
| `--sprint TEXT` | String | None | Set active sprint ID |
| `--db TEXT` | String | db/trackers.sqlite | Database path |

**Examples:**

```powershell
# Set active project
python dbcli.py active set --project P-001

# Set active sprint
python dbcli.py active set --sprint S-2025-08-28

# Set both project and sprint context
python dbcli.py active set --project P-001 --sprint S-2025-08-28

# Set context with custom database
python dbcli.py active set --project P-001 --db custom/trackers.db
```

### Show Active Context

```powershell
python dbcli.py active show [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--db TEXT` | String | db/trackers.sqlite | Database path |

**Examples:**

```powershell
# Show current active context
python dbcli.py active show

# Show context from custom database
python dbcli.py active show --db custom/trackers.db
```

---

## Duplicate Detection

Sub-command: `dups`

The duplicate detection system identifies and helps resolve duplicate or near-duplicate entities.

### Scan for Duplicates

```powershell
python dbcli.py dups scan [ENTITY] [OPTIONS]
```

**Arguments:**

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `ENTITY` | String | task | Entity type to scan |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit INTEGER` | Number | 10 | Max duplicate groups to show |
| `--fuzzy/--no-fuzzy` | Boolean | false | Include fuzzy near-duplicate detection |
| `--threshold FLOAT` | Number | 0.9 | Similarity threshold for fuzzy (0-1) |
| `--max-pairs INTEGER` | Number | 50 | Limit fuzzy pairs displayed |
| `--normalize/--no-normalize` | Boolean | true | Normalize titles for exact grouping |

**Examples:**

```powershell
# Scan for exact task duplicates
python dbcli.py dups scan task

# Scan with fuzzy matching
python dbcli.py dups scan task --fuzzy --threshold 0.8

# Scan without normalization, more results
python dbcli.py dups scan task --no-normalize --limit 20

# High-sensitivity fuzzy scan
python dbcli.py dups scan task --fuzzy --threshold 0.7 --max-pairs 100
```

### Resolve Duplicates

```powershell
python dbcli.py dups resolve [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--keep TEXT` | String | ID of entity to keep |
| `--merge TEXT` | String | Comma-separated IDs to merge |
| `--strategy TEXT` | String | Resolution strategy (manual, auto) |

**Examples:**

```powershell
# Manual resolution - keep one, merge others
python dbcli.py dups resolve `
  --keep T-001 `
  --merge T-002,T-003 `
  --strategy manual

# Auto-resolution with specific strategy
python dbcli.py dups resolve `
  --strategy auto `
  --keep "newest"
```

---

## Utility Commands

The utility commands provide system maintenance, validation, and data quality features.

### Validation Commands

```powershell
# Validate all entity relationships
python dbcli.py validate

# Find orphaned entities (broken relationships)
python dbcli.py find-orphans

# Detailed entity views with relationships
python dbcli.py project-details PROJECT_ID
python dbcli.py sprint-details SPRINT_ID
```

### Data Quality Audits

```powershell
# ASCII character audit of CLI source
python dbcli.py ascii-audit

# Scan logs directory for ASCII issues
python dbcli.py logs-ascii-audit [--fix]

# Scan for JSON parse errors in logs
python dbcli.py scan-parse-errors

# Validate logging baseline events
python dbcli.py events-baseline-audit --log logs/events.jsonl
```

**Examples:**

```powershell
# Full system validation
python dbcli.py validate
python dbcli.py find-orphans

# Quality audit pipeline
python dbcli.py ascii-audit
python dbcli.py logs-ascii-audit
python dbcli.py scan-parse-errors
```

---

## Output Formats

The system supports multiple output formats optimized for different use cases.

### Table Format (Default)

Rich-formatted tables with colors, borders, and styling when `--rich-output` is enabled.

**Characteristics:**
- Human-readable with visual styling
- Automatic column sizing
- Color coding for status and priority
- Pagination for large datasets

**Example:**

```powershell
python dbcli.py tasks list
```

### JSON Format

Structured JSON output ideal for machine processing and API integration.

**Characteristics:**
- Complete data structure preservation
- Easy parsing in automation scripts
- Consistent field naming
- Null handling for missing fields

**Example:**

```powershell
python dbcli.py tasks list --format json

# Sample output:
[
  {
    "id": "T-20250828-001",
    "title": "Implement authentication",
    "status": "in_progress",
    "priority": "high",
    "project": "P-001",
    "assignee": "john.doe",
    "created_at": "2025-08-28T10:00:00Z"
  }
]
```

### CSV Format

Comma-separated values for spreadsheet applications and bulk processing.

**Characteristics:**
- Header row with field names
- Consistent delimiter handling
- Excel-compatible formatting
- Suitable for data analysis

**Example:**

```powershell
python dbcli.py tasks list --format csv
```

### JSONL Format (Export Only)

JSON Lines format for streaming data processing and log analysis.

**Characteristics:**
- One JSON object per line
- Streamable for large datasets
- Log-friendly format
- Easy incremental processing

**Example:**

```powershell
python dbcli.py export tasks --format jsonl
```

---

## Best Practices

### For Orchestration Agents

1. **Always Use JSON for Machine Processing**

```powershell
# Correct: Machine-readable output
python dbcli.py --no-rich-output tasks list --format json

# Avoid: Table format for automation
python dbcli.py tasks list  # human-readable only
```

1. **Set Agent Identity for Coordination**

```powershell
# Multi-agent coordination
python dbcli.py --agent-id ORCHESTRATOR-001 tasks create --title "Automated Task"
python dbcli.py --agent-id SCHEDULER-002 tasks update T-001 --status done
```

1. **Handle Errors Properly**

```powershell
# Check exit codes in scripts
python dbcli.py tasks create --title "Test"
if [ $? -ne 0 ]; then
    echo "Task creation failed"
    exit 1
fi
```

1. **Use Filtering to Reduce Output**

```powershell
# Efficient: Filter at source
python dbcli.py tasks list --status active --project P-001 --format json

# Inefficient: Filter after retrieval
python dbcli.py tasks list --format json | jq '.[] | select(.status=="active")'
```

### For Interactive Users

1. **Keep Rich Output Enabled**

```powershell
# Rich formatting for better UX
python dbcli.py tasks list  # default rich output
```

1. **Use Shell Completion**

```powershell
# Install completion for better experience
python dbcli.py --install-completion
```

1. **Preview Before Bulk Operations**

```powershell
# Always preview bulk changes
python dbcli.py workflow bulk-update `
  --entity task `
  --filter "status=old" `
  --set "status=archived" `
  --dry-run
```

### General Guidelines

1. **Data Backup Before Major Changes**

```powershell
# Backup before bulk operations
python dbcli.py export tasks --format json --output backup/tasks_$(date +%Y%m%d).json
python dbcli.py export projects --format json --output backup/projects_$(date +%Y%m%d).json
```

1. **Monitor System Health**

```powershell
# Regular health checks
python dbcli.py status migration
python dbcli.py validate
python dbcli.py workflow status
```

1. **Use Appropriate Log Levels**

```powershell
# Debug for troubleshooting
python dbcli.py --log-level DEBUG tasks show T-001

# INFO for normal operations
python dbcli.py --log-level INFO tasks list
```

---

## Common Patterns

### Task Lifecycle Automation

```powershell
#!/bin/bash
# Complete task workflow

# Create task
TASK_ID=$(python dbcli.py --no-rich-output tasks create `
  --title "Automated Feature Implementation" `
  --project P-001 `
  --sprint S-2025-08-28 `
  --priority high `
  --format json | jq -r '.id')

echo "Created task: $TASK_ID"

# Start work
python dbcli.py tasks update $TASK_ID --status in_progress

# Update progress
python dbcli.py tasks update $TASK_ID --progress 50 --actual-hours 2.0

# Complete task
python dbcli.py tasks update $TASK_ID --status done --actual-hours 4.5

echo "Task $TASK_ID completed"
```

### Project Setup Workflow

```powershell
#!/bin/bash
# Complete project initialization

# Create project
PROJECT_ID=$(python dbcli.py --no-rich-output projects create `
  --name "Website Redesign Q4" `
  --description "Complete website overhaul" `
  --status active `
  --owner "product.manager" `
  --start-date "2025-09-01" `
  --end-date "2025-12-31" `
  --format json | jq -r '.id')

# Create initial sprint
SPRINT_ID=$(python dbcli.py --no-rich-output sprints create `
  --name "Sprint 1 - Discovery" `
  --project $PROJECT_ID `
  --start-date "2025-09-01" `
  --end-date "2025-09-14" `
  --capacity 80.0 `
  --goal "Complete project discovery and planning" `
  --format json | jq -r '.id')

# Set active context
python dbcli.py active set --project $PROJECT_ID --sprint $SPRINT_ID

# Create initial tasks
python dbcli.py tasks create `
  --title "Conduct stakeholder interviews" `
  --project $PROJECT_ID `
  --sprint $SPRINT_ID `
  --priority high `
  --estimated-hours 8.0

python dbcli.py tasks create `
  --title "Analyze current website performance" `
  --project $PROJECT_ID `
  --sprint $SPRINT_ID `
  --priority medium `
  --estimated-hours 4.0

echo "Project $PROJECT_ID initialized with sprint $SPRINT_ID"
```

### Data Export and Backup

```powershell
#!/bin/bash
# Complete data backup workflow

BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Export all entities
python dbcli.py export tasks --format json --output "$BACKUP_DIR/tasks.json"
python dbcli.py export projects --format json --output "$BACKUP_DIR/projects.json"
python dbcli.py export sprints --format json --output "$BACKUP_DIR/sprints.json"

# Export system status
python dbcli.py status migration --format json > "$BACKUP_DIR/migration_status.json"
python dbcli.py workflow status --format json > "$BACKUP_DIR/workflow_status.json"

# Generate manifest
cat > "$BACKUP_DIR/manifest.json" << EOF
{
  "backup_date": "$(date -Iseconds)",
  "files": [
    "tasks.json",
    "projects.json",
    "sprints.json",
    "migration_status.json",
    "workflow_status.json"
  ],
  "format": "json",
  "tool_version": "dbcli.py v1.0"
}
EOF

echo "Backup completed in $BACKUP_DIR"
```

### Bulk Operations Workflow

```powershell
#!/bin/bash
# Safe bulk operations with validation

ENTITY="task"
FILTER="status=new AND priority=low"
SET="status=backlog"

# Preview changes
echo "Previewing bulk update..."
python dbcli.py workflow bulk-update `
  --entity $ENTITY `
  --filter "$FILTER" `
  --set "$SET" `
  --dry-run

# Confirm execution
read -p "Execute bulk update? (y/N): " confirm
if [[ $confirm == [yY] ]]; then
    # Backup first
    python dbcli.py export tasks --format json --output "backup_before_bulk_$(date +%Y%m%d_%H%M%S).json"

    # Execute update
    python dbcli.py workflow bulk-update `
      --entity $ENTITY `
      --filter "$FILTER" `
      --set "$SET" `
      --execute

    echo "Bulk update completed"
else
    echo "Bulk update cancelled"
fi
```

---

## Error Handling

### Exit Codes

| Code | Category | Description | Example Scenarios |
|------|----------|-------------|-------------------|
| 0 | Success | Command completed successfully | Normal operations |
| 1 | General Error | General command failure | Invalid syntax, unexpected errors |
| 2 | Invalid Input | Invalid parameters or arguments | Wrong option values, missing required fields |
| 3 | Data Error | Data validation or integrity error | Constraint violations, invalid relationships |
| 4 | Not Found | Requested entity not found | Non-existent task/project/sprint ID |
| 5 | Permission Error | Insufficient permissions | File access, database permissions |
| 6 | Database Error | Database connection or query error | SQLite corruption, connection failures |

### Error Response Format

**Standard Error (stderr):**

```text
ERROR: Task T-999 not found
```

**JSON Error Response (with --format json):**

```json
{
  "error": true,
  "code": 4,
  "message": "Task T-999 not found",
  "details": {
    "entity": "task",
    "id": "T-999",
    "operation": "show"
  }
}
```

### Error Handling Patterns

**Shell Script Error Handling:**

```powershell
#!/bin/bash
set -e  # Exit on any error

# Function to handle errors
handle_error() {
    local exit_code=$1
    local command="$2"

    case $exit_code in
        0) echo "Success: $command" ;;
        1) echo "General error in: $command" ;;
        2) echo "Invalid input for: $command" ;;
        3) echo "Data error in: $command" ;;
        4) echo "Entity not found in: $command" ;;
        5) echo "Permission error in: $command" ;;
        6) echo "Database error in: $command" ;;
        *) echo "Unknown error ($exit_code) in: $command" ;;
    esac
}

# Execute command with error handling
python dbcli.py tasks show T-001
exit_code=$?
if [ $exit_code -ne 0 ]; then
    handle_error $exit_code "tasks show T-001"
    exit $exit_code
fi
```

**Python Error Handling:**

```python
import subprocess
import json
import sys

def run_dbcli(command, format_json=False):
    """Run dbcli command with error handling."""
    cmd = ["python", "dbcli.py"]
    if format_json:
        cmd.extend(["--no-rich-output"])
    cmd.extend(command)
    if format_json:
        cmd.extend(["--format", "json"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        if format_json:
            return json.loads(result.stdout)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error (code {e.returncode}): {e.stderr}", file=sys.stderr)

        # Handle specific error codes
        if e.returncode == 4:
            print("Entity not found - check ID and try again")
        elif e.returncode == 6:
            print("Database error - check database status")

        raise

# Usage example
try:
    tasks = run_dbcli(["tasks", "list"], format_json=True)
    print(f"Found {len(tasks)} tasks")
except Exception as e:
    print(f"Failed to retrieve tasks: {e}")
    sys.exit(1)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Rich Output Formatting Problems

**Symptoms:**
- Garbled output with escape sequences
- Missing colors or formatting
- Terminal compatibility issues

**Solutions:**

```powershell
# Disable rich output for compatibility
python dbcli.py --no-rich-output tasks list

# Check terminal environment
export TERM=xterm-256color
export COLORTERM=truecolor

# Force specific encoding
export PYTHONIOENCODING=utf-8
```

#### 2. Database Connection Issues

**Symptoms:**
- "Database not found" errors
- SQLite permission errors
- Migration status failures

**Solutions:**

```powershell
# Check database status
python dbcli.py status migration

# Verify file permissions
ls -la db/trackers.sqlite

# Check CSV directory structure
python dbcli.py --csv-root trackers/csv validate

# Reset database path
python dbcli.py --csv-root /correct/path tasks list
```

#### 3. CSV Migration Problems

**Symptoms:**
- Authority status inconsistencies
- CSV edit blocking errors
- Migration incomplete warnings

**Solutions:**

```powershell
# Check migration status details
python dbcli.py status migration --format json

# Validate entity relationships
python dbcli.py validate

# Reinitialize workflow system
python dbcli.py workflow init --force

# Check for orphaned entities
python dbcli.py find-orphans
```

#### 4. Import/Export Failures

**Symptoms:**
- Import parsing errors
- Export produces empty files
- Format compatibility issues

**Solutions:**

```powershell
# Validate source data format
head -5 source_file.csv

# Check entity structure
python dbcli.py tasks stats
python dbcli.py projects stats

# Test with minimal data
echo "id,title,status" > test.csv
echo "T-TEST,Test Task,new" >> test.csv
python dbcli.py tasks import --file test.csv --format csv

# Export diagnostics
python dbcli.py export tasks --format json | head -10
```

#### 5. Performance Issues

**Symptoms:**
- Slow query responses
- Large output overwhelming terminal
- Memory usage concerns

**Solutions:**

```powershell
# Use limits for large datasets
python dbcli.py tasks list --limit 20

# Apply filters at source
python dbcli.py tasks list --status active --project P-001

# Disable rich output for performance
python dbcli.py --no-rich-output tasks list --format json

# Use streaming export for large datasets
python dbcli.py export tasks --format jsonl > tasks.jsonl
```

### Diagnostic Commands

```powershell
# System health check
python dbcli.py status migration
python dbcli.py validate
python dbcli.py workflow status

# Data quality audit
python dbcli.py ascii-audit
python dbcli.py scan-parse-errors
python dbcli.py find-orphans

# Debug with verbose logging
python dbcli.py --log-level DEBUG tasks show T-001

# Entity relationship verification
python dbcli.py project-details P-001
python dbcli.py sprint-details S-001

# Duplicate detection scan
python dbcli.py dups scan task --limit 5
```

### Performance Optimization

#### For Large Datasets

```powershell
# Use pagination with limits
python dbcli.py tasks list --limit 50

# Filter at database level
python dbcli.py tasks list --status active --project P-001

# Stream exports for bulk data
python dbcli.py export tasks --format jsonl > large_export.jsonl

# Process in batches
for project in $(python dbcli.py projects list --format json | jq -r '.[].id'); do
    python dbcli.py tasks list --project $project --format json > "tasks_$project.json"
done
```

#### For Automation Scripts

```powershell
# Disable unnecessary formatting
python dbcli.py --no-rich-output --log-level ERROR tasks list --format json

# Use specific fields only (when supported)
python dbcli.py tasks list --format json | jq '.[] | {id, title, status}'

# Cache frequently accessed data
python dbcli.py status migration --format json > /tmp/migration_status.json
```

### Environment Troubleshooting

#### Python Environment Issues

```powershell
# Check Python version
python --version

# Verify required packages
python -c "import typer, rich, click; print('All imports successful')"

# Test basic CLI functionality
python dbcli.py --help

# Check environment variables
env | grep -E "(PYTHON|PATH|VIRTUAL_ENV)"
```

#### Database Environment

```powershell
# Check SQLite availability
python -c "import sqlite3; print('SQLite version:', sqlite3.sqlite_version)"

# Test database creation
touch test.db && python -c "import sqlite3; sqlite3.connect('test.db')" && rm test.db

# Verify file system permissions
touch test_permissions && rm test_permissions || echo "Permission denied"
```

#### System Resources

```powershell
# Check disk space
df -h .

# Monitor memory during operations
# Run in separate terminal: watch -n 1 'ps aux | grep dbcli.py'

# Check open file limits
ulimit -n
```

---

**Document Status**: Complete ✅
**Tool Coverage**: 8 sub-applications, 45+ commands documented
**Validation**: Syntax tested against working dbcli.py implementation
**Target Audience**: Orchestrators, automation agents, interactive users
**Last Updated**: August 28, 2025

This comprehensive guide provides complete syntax documentation for all dbcli.py functionality. It is self-contained and ready for orchestrator use without requiring external references or dependencies.
