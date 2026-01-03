# cf_core/cli - Command Line Interface

Typer-based CLI for TaskMan operations.

## Overview

This module provides a unified command-line interface for TaskMan, built with [Typer](https://typer.tiangolo.com/). It supports both human-readable and machine (JSON) output modes.

## Usage

```bash
# Run via module
python -m cf_core.cli.main [command] [options]

# Examples
python -m cf_core.cli.main task list
python -m cf_core.cli.main task create "New Task" --priority high
python -m cf_core.cli.main --machine task list  # JSON output
```

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Module exports |
| `main.py` | Main CLI app with all commands |
| `output.py` | Rich console output formatting |

## Commands

### Task Commands
```bash
task list                        # List all tasks
task create "Title"              # Create task
task get T-001                   # Get task details
task update T-001 --status done  # Update task
task delete T-001                # Delete task
task search "keyword"            # Search tasks
task batch T-001 T-002 --status done  # Bulk update
```

### Sprint Commands
```bash
sprint list                      # List sprints
sprint create "Sprint 1" --start 2025-01-01 --end 2025-01-14
sprint show S-001                # Sprint with progress bar
sprint get S-001                 # Sprint details
```

### System Commands
```bash
health                           # Database health check
```

## Machine Mode

Use `--machine` for JSON output (ideal for AI agents):

```bash
python -m cf_core.cli.main --machine task list
```

Output:
```json
{
  "success": true,
  "data": {
    "tasks": [...],
    "total": 5
  }
}
```

## Configuration

Database path via environment variable:

```bash
export TASKMAN_DB_PATH=/path/to/tasks.sqlite
python -m cf_core.cli.main task list
```

## Testing

```bash
# Integration tests (20 tests)
pytest tests/cf_core/integration/test_cli_integration.py -v
```

## Related

- [Services README](../services/README.md) - Business logic
- [Main cf_core README](../README.md) - Full documentation
