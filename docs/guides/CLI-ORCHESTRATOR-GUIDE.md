# ContextForge CLI Orchestrator Guide

**Version**: 1.2.0 (Updated 2025-08-28)
**Target Audience**: Orchestration Agents, Automation Scripts, Integration Tools
**Scope**: Complete command syntax reference for ContextForge Unified CLI systems

---

## 🎯 Quick Reference

### Primary CLI Tools Available

| CLI Tool | Type | Purpose | Status | Best For |
|----------|------|---------|--------|----------|
| `contextforge_unified_cli_minimal.py` | Python/argparse | Unified operations | ✅ **Production** | **Orchestration** |
| `dbcli.py` | Python/Typer | Database operations | ✅ **Production** | Rich output, advanced features |
| `contextforge_unified_cli.py` | Python/Typer | Unified operations | ❌ **Has Issues** | Not recommended |

### Recommended Tool Selection

**For Orchestration Agents**: Use `contextforge_unified_cli_minimal.py`

- **Pros**: Stable, predictable, comprehensive command set
- **Cons**: Basic table output (no Rich formatting)
- **Direct Invocation**: `python contextforge_unified_cli_minimal.py [command]`

**For Interactive Use**: Use `dbcli.py`

- **Pros**: Rich formatting, comprehensive features, sub-app organization
- **Cons**: More complex command structure
- **Direct Invocation**: `python dbcli.py [command]`

---

## 📋 ContextForge Unified CLI (Minimal) - Primary Tool

**File**: `contextforge_unified_cli_minimal.py`
**Invocation**: `python contextforge_unified_cli_minimal.py [options] [command] [args]`

### Global Options

```bash
-h, --help            # Show help message and exit
-v, --verbose         # Enable verbose logging
```

🚨 **CRITICAL DOCUMENTATION ERROR** 🚨

**TRUST NOTHING VERIFICATION RESULT**: The tool `contextforge_unified_cli_minimal.py` **DOES NOT EXIST** in this repository. All examples below are **NON-FUNCTIONAL**.

**USE INSTEAD**: `python cf_cli.py` (see verified commands section below)

---

### 1. Task Management Commands (⚠️ NON-FUNCTIONAL EXAMPLES)

#### Task List

```bash
# ❌ DOES NOT WORK - TOOL DOES NOT EXIST
python contextforge_unified_cli_minimal.py task list [options]

Options:
  --status STATUS       # Filter by status (todo, in_progress, done, blocked)
  --priority PRIORITY   # Filter by priority (p1, p2, p3, p4)
  --project-id ID       # Filter by project ID
  --sprint-id ID        # Filter by sprint ID
  --limit LIMIT         # Limit number of results (default: 10)
  --format FORMAT       # Output format: table, json, csv (default: table)

Examples:
python contextforge_unified_cli_minimal.py task list --status todo --limit 5
python contextforge_unified_cli_minimal.py task list --project-id P-CORE-001 --format json
python contextforge_unified_cli_minimal.py task list --priority p1 --format csv
```

#### Task Create

```bash
python contextforge_unified_cli_minimal.py task create [options]

Required:
  --title TITLE         # Task title

Optional:
  --description TEXT    # Task description (default: "")
  --status STATUS       # Initial status (default: "todo")
  --priority PRIORITY   # Priority level (default: "p3")
  --project-id ID       # Associated project ID
  --sprint-id ID        # Associated sprint ID
  --assignee USER       # Assigned user
  --story-points POINTS # Story points estimate
  --estimated-hours HOURS # Time estimate

Examples:
python contextforge_unified_cli_minimal.py task create --title "Implement user authentication" --priority p1 --story-points 8
python contextforge_unified_cli_minimal.py task create --title "Fix login bug" --status in_progress --project-id P-WEB-001
```

#### Task Update

```bash
python contextforge_unified_cli_minimal.py task update TASK_ID [options]

Required:
  TASK_ID               # Task ID to update

Optional:
  --status STATUS       # New status
  --priority PRIORITY   # New priority
  --assignee USER       # New assignee
  --story-points POINTS # New story points
  --estimated-hours HOURS # New time estimate
  --actual-hours HOURS  # Actual time spent

Examples:
python contextforge_unified_cli_minimal.py task update T-001 --status done --actual-hours 6.5
python contextforge_unified_cli_minimal.py task update T-002 --priority p1 --assignee john.doe
```

#### Task Metrics

```bash
python contextforge_unified_cli_minimal.py task metrics

# Returns aggregated task statistics and velocity metrics
```

### 2. Project Management Commands

#### Project List

```bash
python contextforge_unified_cli_minimal.py project list [options]

Options:
  --status STATUS       # Filter by status (planned, active, paused, closed)
  --owner OWNER         # Filter by owner
  --limit LIMIT         # Limit number of results (default: 10)
  --format FORMAT       # Output format: table, json, csv (default: table)

Examples:
python contextforge_unified_cli_minimal.py project list --status active
python contextforge_unified_cli_minimal.py project list --owner jane.smith --format json
```

#### Project Create

```bash
python contextforge_unified_cli_minimal.py project create [options]

Required:
  --title TITLE         # Project title

Optional:
  --description TEXT    # Project description (default: "")
  --owner OWNER         # Project owner
  --status STATUS       # Initial status (default: "planned")
  --start-date DATE     # Start date (YYYY-MM-DD)
  --end-date DATE       # End date (YYYY-MM-DD)
  --kpi-primary KPI     # Primary KPI

Examples:
python contextforge_unified_cli_minimal.py project create --title "Website Redesign" --owner tech.lead --start-date 2025-09-01
python contextforge_unified_cli_minimal.py project create --title "API Integration" --status active --kpi-primary "API response time < 200ms"
```

#### Project Update

```bash
python contextforge_unified_cli_minimal.py project update PROJECT_ID [options]

Required:
  PROJECT_ID            # Project ID to update

Optional:
  --status STATUS       # New status
  --owner OWNER         # New owner
  --end-date DATE       # New end date

Examples:
python contextforge_unified_cli_minimal.py project update P-WEB-001 --status active
python contextforge_unified_cli_minimal.py project update P-API-002 --end-date 2025-12-31
```

### 3. Sprint Management Commands

#### Sprint List

```bash
python contextforge_unified_cli_minimal.py sprint list [options]

Options:
  --status STATUS       # Filter by status (planned, active, completed)
  --project-id ID       # Filter by project ID
  --limit LIMIT         # Limit number of results (default: 10)
  --format FORMAT       # Output format: table, json, csv (default: table)

Examples:
python contextforge_unified_cli_minimal.py sprint list --status active
python contextforge_unified_cli_minimal.py sprint list --project-id P-CORE-001 --format json
```

#### Sprint Create

```bash
python contextforge_unified_cli_minimal.py sprint create [options]

Required:
  --title TITLE         # Sprint title
  --project-id ID       # Project ID

Optional:
  --goal TEXT           # Sprint goal
  --status STATUS       # Initial status (default: "planned")
  --start-date DATE     # Start date (YYYY-MM-DD)
  --end-date DATE       # End date (YYYY-MM-DD)
  --committed-points POINTS # Committed story points
  --capacity-points POINTS  # Capacity points

Examples:
python contextforge_unified_cli_minimal.py sprint create --title "Sprint 1" --project-id P-WEB-001 --goal "User login functionality"
python contextforge_unified_cli_minimal.py sprint create --title "Sprint 2" --project-id P-API-002 --committed-points 40 --capacity-points 45
```

#### Sprint Update

```bash
python contextforge_unified_cli_minimal.py sprint update SPRINT_ID [options]

Required:
  SPRINT_ID             # Sprint ID to update

Optional:
  --status STATUS       # New status
  --committed-points POINTS # New committed points
  --capacity-points POINTS  # New capacity points
  --end-date DATE       # New end date

Examples:
python contextforge_unified_cli_minimal.py sprint update S-001 --status active
python contextforge_unified_cli_minimal.py sprint update S-002 --committed-points 35 --end-date 2025-09-15
```

#### Sprint Metrics

```bash
python contextforge_unified_cli_minimal.py sprint metrics [options]

Optional:
  --sprint-id ID        # Specific sprint ID (optional, shows all if not specified)

Examples:
python contextforge_unified_cli_minimal.py sprint metrics
python contextforge_unified_cli_minimal.py sprint metrics --sprint-id S-001
```

### 4. Velocity Tracking Commands

#### Velocity Predict

```bash
python contextforge_unified_cli_minimal.py velocity predict [options]

Required:
  --story-points POINTS # Story points to predict

Optional:
  --complexity MULTIPLIER # Complexity multiplier (default: 1.0, range: 0.5-3.0)

Examples:
python contextforge_unified_cli_minimal.py velocity predict --story-points 20
python contextforge_unified_cli_minimal.py velocity predict --story-points 15 --complexity 1.5
```

### 5. CSV Migration Commands

#### Migration List

```bash
python contextforge_unified_cli_minimal.py migrate list [options]

Optional:
  --format FORMAT       # Output format: table, json (default: table)

Examples:
python contextforge_unified_cli_minimal.py migrate list
python contextforge_unified_cli_minimal.py migrate list --format json
```

#### Migration Validate

```bash
python contextforge_unified_cli_minimal.py migrate validate ENTITY_TYPE [options]

Required:
  ENTITY_TYPE           # Entity type: actions, labels, risks, acceptance, etc.

Optional:
  --format FORMAT       # Output format: table, json (default: table)

Examples:
python contextforge_unified_cli_minimal.py migrate validate actions
python contextforge_unified_cli_minimal.py migrate validate labels --format json
```

#### Migration Import

```bash
python contextforge_unified_cli_minimal.py migrate import ENTITY_TYPE [options]

Required:
  ENTITY_TYPE           # Entity type to import

Optional:
  --dry-run             # Preview import without executing
  --backup              # Create JSON backup (default: true)

Examples:
python contextforge_unified_cli_minimal.py migrate import actions --dry-run
python contextforge_unified_cli_minimal.py migrate import labels --backup
```

#### Migration Status

```bash
python contextforge_unified_cli_minimal.py migrate status [options]

Optional:
  --format FORMAT       # Output format: table, json (default: table)

Examples:
python contextforge_unified_cli_minimal.py migrate status
python contextforge_unified_cli_minimal.py migrate status --format json
```

### 6. Entity Management Commands

#### Actions List

```bash
python contextforge_unified_cli_minimal.py actions list [options]

Optional:
  --task-id ID          # Filter by task ID
  --limit LIMIT         # Limit number of results (default: 20)
  --format FORMAT       # Output format: table, json (default: table)

Examples:
python contextforge_unified_cli_minimal.py actions list --limit 10
python contextforge_unified_cli_minimal.py actions list --task-id T-001 --format json
```

#### Labels List

```bash
python contextforge_unified_cli_minimal.py labels list [options]

Optional:
  --task-id ID          # Filter by task ID
  --limit LIMIT         # Limit number of results (default: 20)
  --format FORMAT       # Output format: table, json (default: table)

Examples:
python contextforge_unified_cli_minimal.py labels list
python contextforge_unified_cli_minimal.py labels list --task-id T-002 --format json
```

#### Risks List

```bash
python contextforge_unified_cli_minimal.py risks list [options]

Optional:
  --task-id ID          # Filter by task ID
  --limit LIMIT         # Limit number of results (default: 20)
  --format FORMAT       # Output format: table, json (default: table)

Examples:
python contextforge_unified_cli_minimal.py risks list --limit 5
python contextforge_unified_cli_minimal.py risks list --task-id T-003 --format json
```

### 7. Version Information

```bash
python contextforge_unified_cli_minimal.py version

# Returns comprehensive capability information
```

---

## 🔧 CF_CLI Reference (Advanced Features)

**File**: `cf_cli.py`
**Invocation**: `python cf_cli.py [global_options] [command] [args]`

### Global Options

```bash
--csv-root PATH         # CSV data directory (default: trackers\csv)
--log-level LEVEL       # Logging level (default: INFO)
--log-path PATH         # Custom log file
--rich-output           # Enable rich console (default: enabled)
--no-rich-output        # (DEPRECATED) Previously disabled rich console; rich output is now mandatory and this flag will be removed in a future release
--verify                # Enable verification (default: enabled)
--no-verify             # Disable verification
--agent-id ID           # Agent identity tag for multi-agent coordination
```

### Command Categories

#### Task Commands

⚠️ **TRUST VERIFIED 2025-10-02** - Commands below verified against actual CF_CLI help output

```bash
# VERIFIED WORKING COMMANDS
python cf_cli.py task list [options]        # ✅ VERIFIED
python cf_cli.py task show TASK_ID          # ✅ VERIFIED
python cf_cli.py task create [options]      # ✅ VERIFIED
python cf_cli.py task update TASK_ID [options]  # ✅ VERIFIED
python cf_cli.py task upsert [options]      # ✅ VERIFIED
python cf_cli.py task complete TASK_ID      # ✅ VERIFIED (mark task done)
python cf_cli.py task enhance TASK_ID       # ✅ VERIFIED (append notes)
python cf_cli.py task status-counts         # ✅ VERIFIED (aggregate by status)

# DIAGNOSTIC COMMANDS
python cf_cli.py task rich-mode             # Toggle Rich output mode
python cf_cli.py task diag-rich             # Rich configuration diagnostic
python cf_cli.py task tasksync              # TaskSync process monitoring
```

**❌ REMOVED COMMANDS** (documented but don't exist):
- `task get` → Use `task show` instead
- `task details` → Use `task show` instead
- `task stats` → Use `task status-counts` instead
- `task delete`, `task backfill-agent-id`, `task import`, `task export-csv` → Not available

#### Project Commands

```bash
python cf_cli.py project list [options]
python cf_cli.py project show PROJECT_ID
python cf_cli.py project create [options]
python cf_cli.py project update PROJECT_ID [options]
python cf_cli.py project upsert [options]
python cf_cli.py project delete PROJECT_ID
```

#### Sprint Commands

```bash
python cf_cli.py sprint list [options]
python cf_cli.py sprint show SPRINT_ID
python cf_cli.py sprint create [options]
python cf_cli.py sprint update SPRINT_ID [options]
python cf_cli.py sprint upsert [options]
python cf_cli.py sprint delete SPRINT_ID
python cf_cli.py sprint stats
python cf_cli.py sprint complete SPRINT_ID
```

#### Status Commands

```bash
python cf_cli.py status migration        # Show CSV→SQLite migration status
```

#### Export Commands

```bash
python cf_cli.py export tasks [options]
python cf_cli.py export projects [options]
python cf_cli.py export sprints [options]
```

#### Workflow Commands

```bash
python cf_cli.py workflow [subcommands]   # Workflow automation features
```

#### Active Context Commands

```bash
python cf_cli.py context [subcommands]     # Manage active project/sprint context
```

#### Utility Commands

```bash
python cf_cli.py validate                 # Validate relationship integrity
python cf_cli.py find-orphans            # Find entities with broken relationships
python cf_cli.py dups [subcommands]      # Duplicate detection
python cf_cli.py project-details PROJECT_ID  # Detailed project information
python cf_cli.py sprint-details SPRINT_ID    # Detailed sprint information
```

---

## 🚀 Orchestration Best Practices

### 1. Command Invocation Patterns

**Direct Python Invocation (Recommended)**:

```bash
python contextforge_unified_cli_minimal.py [command] [args]
python cf_cli.py [command] [args]
```

**Environment Validation**:

```bash
# Ensure Python environment is activated
python --version  # Should return Python 3.11+
```

### 2. Output Format Selection

**For Machine Processing**: Use `--format json`

```bash
python contextforge_unified_cli_minimal.py task list --format json | jq '.[] | .id'
```

**For Human Review**: Use `--format table` (default)

```bash
python contextforge_unified_cli_minimal.py task list --format table
```

**For Data Export**: Use `--format csv`

```bash
python contextforge_unified_cli_minimal.py task list --format csv > tasks_export.csv
```

### 3. Error Handling

**Exit Codes**:

- `0`: Success
- `1`: Generic failure
- `2`: Validation/config error
- `3`: Quality gate failure
- `4`: Dependency/tool missing

**Error Detection Pattern**:

```bash
python contextforge_unified_cli_minimal.py task create --title "Test Task"
if [ $? -eq 0 ]; then
    echo "Task created successfully"
else
    echo "Task creation failed with exit code $?"
fi
```

### 4. Logging and Observability

**Structured Logs**: Available in `logs/unified_cli.jsonl`

```bash
# View recent log entries
tail -f logs/unified_cli.jsonl | jq .
```

**Verbose Mode**: Use `-v` for detailed operation logging

```bash
python contextforge_unified_cli_minimal.py -v task list --status todo
```

### 5. Data Flow Patterns

**Typical Orchestration Sequence**:

```bash
# 1. Check current status
python contextforge_unified_cli_minimal.py task list --status todo --limit 5

# 2. Create new task
python contextforge_unified_cli_minimal.py task create \
  --title "New Feature Implementation" \
  --priority p1 \
  --project-id P-CORE-001 \
  --story-points 8

# 3. Update task progress
python contextforge_unified_cli_minimal.py task update T-NEW-001 \
  --status in_progress \
  --assignee automation.agent

# 4. Complete task
python contextforge_unified_cli_minimal.py task update T-NEW-001 \
  --status done \
  --actual-hours 6.5

# 5. Get velocity metrics
python contextforge_unified_cli_minimal.py velocity predict --story-points 20
```

### 6. Integration Considerations

**Multi-Agent Coordination**: Use `--agent-id` in dbcli

```bash
python dbcli.py --agent-id AGENT-ORCHESTRATOR tasks list
```

**Concurrent Safety**: Commands are designed to be idempotent

```bash
# Safe to retry operations
python contextforge_unified_cli_minimal.py task update T-001 --status done
```

**Data Validation**: Use migration commands for data integrity

```bash
python contextforge_unified_cli_minimal.py migrate status
```

---

## ⚠️ Common Gotchas for Orchestrators

### 1. Tool Selection

- ❌ **DON'T**: Use `contextforge_unified_cli.py` (has compatibility issues)
- ✅ **DO**: Use `contextforge_unified_cli_minimal.py` for orchestration
- ✅ **DO**: Use `dbcli.py` for advanced features and rich output

### 2. Parameter Formatting

- ❌ **DON'T**: Use spaces in IDs: `"T 001"`
- ✅ **DO**: Use hyphens/underscores: `"T-001"` or `"T_001"`

### 3. Date Formats

- ❌ **DON'T**: Use ambiguous dates: `"01/02/2025"`
- ✅ **DO**: Use ISO format: `"2025-01-02"`

### 4. Status Values

- **Tasks**: `todo`, `in_progress`, `done`, `blocked`
- **Projects**: `planned`, `active`, `paused`, `closed`
- **Sprints**: `planned`, `active`, `completed`

### 5. Priority Values

- Use: `p1` (highest), `p2`, `p3`, `p4` (lowest)
- ❌ **DON'T**: Use: `high`, `medium`, `low`

### 6. Output Processing

- Always specify `--format json` for machine processing
- Parse JSON output with proper error handling
- Check exit codes before processing output

---

## 📊 Example Automation Scripts

### Task Management Automation

```bash
#!/bin/bash
# Create and track a development task

TASK_ID=$(python contextforge_unified_cli_minimal.py task create \
  --title "Implement user authentication" \
  --priority p1 \
  --project-id P-WEB-001 \
  --story-points 8 \
  --format json | jq -r '.id')

echo "Created task: $TASK_ID"

# Start working on task
python contextforge_unified_cli_minimal.py task update $TASK_ID \
  --status in_progress \
  --assignee automation.agent

# Complete task
python contextforge_unified_cli_minimal.py task update $TASK_ID \
  --status done \
  --actual-hours 7.5

echo "Task $TASK_ID completed"
```

### Sprint Management Automation

```bash
#!/bin/bash
# Sprint planning automation

# Get active tasks
ACTIVE_TASKS=$(python contextforge_unified_cli_minimal.py task list \
  --status todo \
  --priority p1 \
  --format json)

echo "Found $(echo $ACTIVE_TASKS | jq length) high-priority tasks"

# Create new sprint
SPRINT_ID=$(python contextforge_unified_cli_minimal.py sprint create \
  --title "Development Sprint $(date +%Y-%m-%d)" \
  --project-id P-CORE-001 \
  --committed-points 40 \
  --capacity-points 45 \
  --format json | jq -r '.id')

echo "Created sprint: $SPRINT_ID"

# Get sprint metrics
python contextforge_unified_cli_minimal.py sprint metrics --sprint-id $SPRINT_ID
```

---

## 🔗 Related Resources

- **CSV Migration Guide**: See migration commands section for data import procedures
- **Velocity Tracking**: Use velocity predict for time estimation (proven 0.44 hours/point baseline)
- **Structured Logging**: Monitor `logs/unified_cli.jsonl` for operation traceability
- **Database Integration**: Both CLIs support unified database backend
- **Multi-Format Output**: JSON, CSV, and table formats for different consumption needs

---

**Last Updated**: 2025-08-28
**CLI Version**: contextforge_unified_cli_minimal.py v1.2.0-minimal
**Maintenance**: Update this guide when new commands or options are added
