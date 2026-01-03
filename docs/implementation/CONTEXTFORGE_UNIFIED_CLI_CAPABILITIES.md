# ContextForge Unified CLI - Capabilities Consolidation Map

## Overview

The `contextforge_unified_cli.py` consolidates ALL CLI functionality across the workspace into a single comprehensive interface, replacing multiple scattered command-line tools with a unified Typer-based API.

## Consolidated CLI Sources

### 1. Primary CLIs Replaced

| Original CLI | Size | Framework | Key Features | Status |
|-------------|------|-----------|--------------|---------|
| `dbcli.py` | 6,221 lines | Typer | 8 sub-apps (tasks, projects, sprints, workflow, export, status, active, duplicates) | ✅ Core functionality integrated |
| `simple_task_cli.py` | 268 lines | argparse | Basic task CRUD with CSV backend | ✅ Fully integrated |
| `working_cli.py` | 314 lines | argparse | SQLite-based task management with Rich output | ✅ Backend support planned |
| `cf_tracker_cli.py` | 108 lines | argparse | JSON-based tracker management | ✅ Tracker sub-app created |

### 2. Python Module CLIs

| Module | Location | Framework | Key Features | Status |
|--------|----------|-----------|--------------|---------|
| `cli/python/cf_tracker/cli.py` | 341 lines | Typer | Multi-backend tracker system (markdown/duckdb/sqlite/postgres) | ✅ Integrated as tracker sub-app |
| Various orchestration CLIs | `python/` directory | Mixed | Analytics, migration, validation | 🚧 Integration planned |

### 3. PowerShell CLIs

| PowerShell CLI | Framework | Key Features | Status |
|----------------|-----------|--------------|---------|
| `TaskManagement.psm1` | Advanced Functions | 7 core functions: Get-TaskSummary, Get-ActiveTasks, Update-TaskStatus, Start-TaskExecution, Complete-TaskExecution, Get-TaskMetrics, Search-Tasks | ✅ All functions ported to Python |
| `Invoke-VelocityTracker.ps1` | Advanced Function | DuckDB velocity tracking with Record/Predict/Report actions | ✅ Velocity sub-app implemented |
| Various `cli/*.ps1` scripts | 866 PowerShell files | Specialized governance, quality, and automation tasks | 🚧 Governance sub-app created |

## Unified CLI Structure

```text
contextforge [global-options]
├── task                    # Task management (consolidates 4 CLIs)
│   ├── list               # List tasks with filtering
│   ├── create             # Create new tasks
│   ├── update             # Update task status/progress
│   ├── start              # Start task execution (from TaskManagement.psm1)
│   ├── complete           # Complete tasks with metrics (from TaskManagement.psm1)
│   ├── search             # Search tasks by criteria (from TaskManagement.psm1)
│   └── metrics            # Generate task analytics (from TaskManagement.psm1)
├── project                # Project management (from dbcli.py)
│   ├── list
│   ├── create
│   └── [other project ops]
├── sprint                 # Sprint management (from dbcli.py)
│   ├── list
│   ├── create
│   └── [other sprint ops]
├── velocity               # DuckDB velocity tracking (from Invoke-VelocityTracker.ps1)
│   ├── record             # Record velocity data
│   ├── predict            # Predict completion times
│   └── report             # Generate velocity reports
├── gov                    # Governance operations (from governance scripts)
│   ├── compliance
│   └── [other gov ops]
├── tracker                # Multi-backend tracker (from cf_tracker CLI)
│   ├── status
│   └── [other tracker ops]
└── version                # Version and consolidation info
```

## Backend Support Matrix

| Backend | Tasks | Projects | Sprints | Velocity | Tracker |
|---------|-------|----------|---------|----------|---------|
| CSV | ✅ Implemented | 🚧 Planned | 🚧 Planned | N/A | 🚧 Planned |
| SQLite | 🚧 Planned | 🚧 Planned | 🚧 Planned | N/A | ✅ Supported |
| YAML | 🚧 Planned | 🚧 Planned | 🚧 Planned | N/A | 🚧 Planned |
| DuckDB | N/A | N/A | N/A | ✅ Integrated | ✅ Supported |
| Markdown | N/A | N/A | N/A | N/A | ✅ Supported |
| PostgreSQL | N/A | N/A | N/A | N/A | ✅ Supported |

## Key Features Consolidated

### Task Management (Multi-CLI Consolidation)

From `dbcli.py` tasks sub-app:
- Rich table rendering
- JSON/CSV output formats
- Comprehensive filtering
- Artifact emission

From `simple_task_cli.py`:
- CSV backend support
- Basic CRUD operations
- Clean data handling

From `working_cli.py`:
- SQLite backend support
- Rich console output
- Direct database queries

From `TaskManagement.psm1`:
- Task execution lifecycle (Start-TaskExecution, Complete-TaskExecution)
- Progress tracking with metrics
- Status transitions with validation
- Comprehensive search capabilities
- Automatic JSONL logging
- Performance analytics

### Velocity Tracking (PowerShell → Python Port)

From `Invoke-VelocityTracker.ps1`:
- DuckDB-based velocity analytics
- Story point prediction (proven 0.44 hours/point baseline)
- Complexity multipliers (0.5-3.0 range)
- Historical data import capabilities
- Sacred Geometry complexity scoring integration

### Multi-Backend Tracker System

From `cli/python/cf_tracker/cli.py`:
- Backend abstraction (markdown/duckdb/sqlite/postgres)
- Entity operations (projects, sprints, tasks)
- Tool evaluation matrices
- Heartbeat tracking

## Logging & Observability

### Unified Logging Standard
- All operations emit structured JSONL logs to `logs/unified_cli.jsonl`
- Event types: `command_start`, `command_success`, `command_error`, `task_execution_started`, `task_execution_completed`, `velocity_data_recorded`, etc.
- Consistent timestamp format (ISO 8601 UTC)
- Error handling with context preservation

### Metric Emission
- Task completion rates
- Velocity predictions with confidence levels
- Time tracking and variance analysis
- Backend performance metrics

## Installation & Usage

### Prerequisites

```bash
# Install required Python packages
pip install typer rich

# Ensure workspace structure exists
mkdir -p logs db trackers/csv build/artifacts/json
```

### Basic Usage Examples

```bash
# List all tasks
python contextforge_unified_cli.py task list

# Create a new task
python contextforge_unified_cli.py task create --title "Implement feature X" --priority 1

# Start working on a task
python contextforge_unified_cli.py task start T-20250827-001

# Complete a task with time tracking
python contextforge_unified_cli.py task complete T-20250827-001 --actual-hours 2.5

# Search tasks
python contextforge_unified_cli.py task search "feature" --field title

# Record velocity data
python contextforge_unified_cli.py velocity record --task-id T-20250827-001 --hours 2.5 --story-points 5

# Predict completion time
python contextforge_unified_cli.py velocity predict --story-points 8 --complexity 1.2

# Show version and consolidation info
python contextforge_unified_cli.py version
```

### Output Format Options
- `--format table` - Rich formatted tables (default)
- `--format json` - JSON output for machine consumption
- `--format csv` - CSV output for spreadsheet import

### Backend Selection
- `--backend csv` - CSV file backend (default for tasks)
- `--backend sqlite` - SQLite database backend
- `--backend yaml` - YAML file backend

## Migration Path

### Phase 1: Core Task Operations ✅ Complete
- Basic task CRUD operations
- CSV backend support
- Task execution lifecycle
- Velocity tracking integration

### Phase 2: Multi-Backend Support 🚧 In Progress
- SQLite backend implementation
- YAML backend implementation
- Backend migration utilities

### Phase 3: Full Entity Support 🚧 Planned
- Complete project operations
- Complete sprint operations
- Governance operations integration
- Quality gates integration

### Phase 4: Advanced Features 🚧 Planned
- REST API endpoints
- Web dashboard integration
- Advanced analytics
- Multi-user support

## Compliance & Quality

### ContextForge Universal Methodology Alignment
- Sacred Geometry shape progression support
- Evidence tracking integration
- Logging First principle compliance
- Workspace First mandate adherence

### Code Quality
- Type hints throughout
- Error handling with context
- Structured logging
- Rich console output for UX

### Testing Strategy
- Unit tests for core functions
- Integration tests for backends
- CLI interaction tests
- Performance benchmarks

## Deprecation Timeline

| Original CLI | Deprecation Status | Timeline | Notes |
|-------------|-------------------|----------|-------|
| `simple_task_cli.py` | ✅ Deprecated | Immediate | All functionality in unified CLI |
| `working_cli.py` | 🚧 Deprecation planned | After SQLite backend complete | Maintain until parity confirmed |
| `cf_tracker_cli.py` | 🚧 Deprecation planned | After tracker sub-app complete | Basic functionality ported |
| `TaskManagement.psm1` | 🚧 Keep for legacy | Long-term | PowerShell ecosystem still needs PS functions |
| `Invoke-VelocityTracker.ps1` | 🚧 Deprecation planned | After velocity sub-app mature | DuckDB integration needs validation |
| `dbcli.py` | 🚧 Gradual migration | Phased approach | Large codebase requires careful migration |

## Benefits of Consolidation

### For Users
- Single CLI to learn and use
- Consistent command syntax across all operations
- Unified help system and documentation
- Better discoverability of features

### For Developers
- Reduced maintenance overhead
- Consistent error handling and logging
- Shared backend abstractions
- Easier testing and validation

### For Operations
- Simplified deployment (single script)
- Unified logging and monitoring
- Consistent configuration management
- Better automation integration

## Future Enhancements

1. **REST API Server**: Add FastAPI server mode for web integration
2. **Configuration Management**: Unified config file support
3. **Plugin System**: Allow custom command extensions
4. **Performance Optimization**: Async operations for large datasets
5. **Multi-User Support**: Authentication and authorization
6. **Workspace Synchronization**: Multi-machine sync capabilities
7. **Advanced Analytics**: ML-powered velocity predictions
8. **Integration Hub**: Connect with external systems (Jira, GitHub, etc.)

---

*This consolidation represents a major step toward the ContextForge Universal Methodology goal of unified, observable, and maintainable automation infrastructure.*
