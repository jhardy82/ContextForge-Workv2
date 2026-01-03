# Database Authority User Guide

## Overview

The Database Authority system establishes `dbcli.py` as the single source of truth for task, sprint, and project management. CSV files are treated as read-only exports with authority headers that discourage direct editing.

## Key Concepts

### Authority Model
- **dbcli.py**: Authoritative interface for all CRUD operations
- **CSV files**: Read-only exports with warning headers
- **DB_AUTHORITY.SENTINEL**: Sentinel file indicating authority is active
- **Drift Detection**: Monitoring system for unauthorized CSV modifications

### Command Structure

```
python dbcli.py <category> <action> [options]
```

## Core Commands

### Task Management

```bash
# List tasks
python dbcli.py task list [--status <status>] [--priority <priority>] [--limit <n>]

# Start working on a task
python dbcli.py task start <task_id>

# Complete a task
python dbcli.py task complete <task_id> --notes "Implementation details"

# Create a new task (if available)
python dbcli.py task create --title "Task Title" --priority <priority>
```

### Status and Authority Commands

```bash
# Check migration status
python dbcli.py status migration

# Check system health
python dbcli.py status health

# Validate authority compliance
python dbcli.py status validate

# Repair CSV files (add authority headers)
python dbcli.py status repair [--dry-run]
```

### Drift Detection

```bash
# One-time drift check
python dbcli.py drift check [--json]

# Continuous monitoring
python dbcli.py drift monitor [--interval <seconds>] [--duration <minutes>]
```

## Authority Headers

CSV files include warning headers to discourage direct editing:

```
### OBSOLETE (Read-Only) – Task management has migrated; use `python dbcli.py task ...`.
### Direct edits discouraged and may produce `direct_csv_write_blocked` decision events.
```

## Workflow Transition

### Before Database Authority
1. Edit CSV files directly
2. Manual synchronization between systems
3. Risk of data conflicts and inconsistencies

### After Database Authority
1. Use `python dbcli.py` commands exclusively
2. CSV files automatically updated with authority headers
3. Drift detection prevents unauthorized modifications
4. Consistent logging and audit trail

## Common Operations

### Daily Task Management

```bash
# Check what tasks need attention
python dbcli.py task list --status in_progress

# Start working on a task
python dbcli.py task start T-20250829-001

# Complete when done
python dbcli.py task complete T-20250829-001 --notes "Implemented feature X with tests"
```

### Authority Maintenance

```bash
# Weekly authority check
python dbcli.py status validate

# If issues found, repair
python dbcli.py status repair

# Monitor for drift during critical periods
python dbcli.py drift monitor --duration 60
```

### System Health Monitoring

```bash
# Check overall system status
python dbcli.py status health

# Verify migration is complete
python dbcli.py status migration

# Scan for compliance issues
python dbcli.py drift check --json
```

## Troubleshooting

### Missing Authority Headers
**Symptom**: `python dbcli.py status validate` shows warnings about missing headers
**Solution**: Run `python dbcli.py status repair`

### CSV Parsing Errors
**Symptom**: Task operations fail with CSV parsing errors
**Cause**: Corrupted authority headers or direct CSV edits
**Solution**:
1. Run `python dbcli.py status repair`
2. If problem persists, check CSV file structure manually

### Drift Detection Alerts
**Symptom**: `python dbcli.py drift check` shows violations
**Cause**: Direct CSV file modifications outside dbcli
**Solution**:
1. Identify source of modifications
2. Use dbcli commands instead of direct edits
3. Run `python dbcli.py status repair` to restore authority headers

### Command Not Found
**Symptom**: `No such option` or command errors
**Cause**: Using deprecated flags or incorrect syntax
**Solution**: Check `python dbcli.py <command> --help` for current options

## Best Practices

### Do's ✅
- Always use `python dbcli.py` commands for task management
- Run `python dbcli.py status validate` regularly
- Use `--json` flags when integrating with other tools
- Include detailed notes when completing tasks
- Monitor drift during collaborative work periods

### Don'ts ❌
- Never edit CSV files directly
- Don't ignore authority validation warnings
- Avoid bypassing the dbcli interface
- Don't remove authority headers manually
- Don't use deprecated command flags

## Integration Examples

### PowerShell Integration

```powershell
# Get task status in PowerShell
$taskStatus = python dbcli.py task list --json | ConvertFrom-Json

# Complete task with PowerShell
python dbcli.py task complete $taskId --notes "Automated completion from PowerShell"
```

### Automation Scripts

```bash
#!/bin/bash
# Daily authority health check
python dbcli.py status validate --json > daily_health.json
if [ $? -ne 0 ]; then
    python dbcli.py status repair
    python dbcli.py drift check --json > drift_report.json
fi
```

## Migration Guide

### From Direct CSV Editing
1. **Stop**: Cease all direct CSV file modifications
2. **Validate**: Run `python dbcli.py status validate`
3. **Repair**: Fix any compliance issues with `python dbcli.py status repair`
4. **Learn**: Familiarize yourself with dbcli commands
5. **Monitor**: Use drift detection to catch any remaining direct edits

### From Legacy Systems
1. **Backup**: Create backups of existing CSV files
2. **Import**: Ensure all data is imported into the dbcli system
3. **Validate**: Verify data integrity with status commands
4. **Train**: Update team workflows to use dbcli commands
5. **Enforce**: Enable drift monitoring to detect violations

## Support and Maintenance

### Regular Maintenance Tasks
- Weekly: `python dbcli.py status validate`
- Monthly: Review drift detection logs
- Quarterly: Update authority headers if schema changes

### Performance Optimization
- Use `--limit` flags for large task lists
- Enable `--json` output for automated processing
- Monitor drift detection intervals based on team size

### Security Considerations
- Authority headers prevent accidental data corruption
- Drift detection provides audit trail for unauthorized changes
- Structured logging enables compliance reporting

## Version History

- v1.0: Initial Database Authority implementation
- v1.1: Added drift detection commands
- v1.2: Enhanced status validation and repair functionality

---

For additional support or feature requests, refer to the project documentation or create a task using:

```bash
python dbcli.py task create --title "Support Request: <description>" --priority medium
```
