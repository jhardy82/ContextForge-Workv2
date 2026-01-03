# dbcli to CF_CORE Migration Plan

**Date**: 2025-11-17
**Status**: Phase 1 Planning Complete
**Priority**: 🔥 CRITICAL - Strategic CLI Consolidation
**Timeline**: Q2-Q3 2026

---

## Executive Summary

**Strategic Goal**: Migrate all dbcli functionality into the unified **CF_Core CLI** as part of the broader CLI consolidation initiative, then archive dbcli after full validation.

**Current State**: dbcli is a **legacy production CLI** (✅ Status: Production) with ~3,000 lines of database operations code.

**Target State**: dbcli functionality fully integrated into CF_Core CLI as the `db` plugin, with dbcli archived after 6-week deprecation period.

---

## Strategic Context

### From: 15-Future-Roadmap.md

#### CLI Consolidation Status (Lines 79-88)

**Current**: 5 fragmented CLIs (~12,300 lines scattered code)
- cf_cli (fragments) - Task management, context operations
- **dbcli** - Database operations
- TaskMan CLI - Task CRUD via API
- Legacy scripts - Ad-hoc utilities (deprecated)
- Velocity CLI - Analytics queries

**Target**: CF_Core CLI as PRIMARY unified interface (Phase 1 planning complete)

#### Deprecation Timeline (Lines 936-953)

| Quarter | Component | Action | Status |
|---------|-----------|--------|--------|
| **Q2 2026** | **dbcli** | Wrapper with deprecation warnings | Planned |
| **Q2 2026** | TaskMan CLI | Wrapper with deprecation warnings | Planned |
| **Q2 2026** | Velocity CLI | Integration into cf-core | Planned |
| **Q3 2026** | Legacy scripts | Archive or migrate | Planned |
| **Q3 2026** | All wrappers | Remove after 6-week grace period | Planned |

**Transition Support**:
- 6-week deprecation warnings
- Automated migration scripts
- Comprehensive migration guides
- Internal training sessions

### From: CF-CORE-CLI-Consolidation-Plan.md

#### Output Consolidation (Week 1-4)

**Goal**: Consolidate OutputManager + DisplayManager into unified `cf_core/cli/output.py`

**Benefit for dbcli Migration**:
- Single output format API for all commands
- Consistent `--format` flag (table|json|jsonl)
- Result monad integration for error handling
- Standardized output across all plugins

---

## Migration Architecture

### Current dbcli Structure

```
python/dbcli/
├── app.py                   # Main Typer app (~800 lines)
├── plugins.py               # Plugin interface
├── tasks_commands.py        # Task-related db operations
├── unified_db.py            # Database abstraction
└── [additional commands]

Total: ~3,000 lines
```

### Target CF_Core CLI Structure

```
cf_core/cli/
├── output.py               # Unified output module (Week 1)
└── plugins/
    └── db/                 # Database plugin (migrated from dbcli)
        ├── __init__.py     # Plugin registration
        ├── commands.py     # All db commands
        ├── query.py        # Query operations
        ├── admin.py        # Admin operations
        └── validation.py   # Validation commands (from validation swarm)
```

### Command Mapping

| dbcli Command | CF_Core CLI Equivalent | Status |
|---------------|------------------------|--------|
| `dbcli task create` | `cf-core db task create` | To Migrate |
| `dbcli task list` | `cf-core db task list` | To Migrate |
| `dbcli task update` | `cf-core db task update` | To Migrate |
| `dbcli sprint status` | `cf-core db sprint status` | To Migrate |
| `dbcli project list` | `cf-core db project list` | To Migrate |
| `dbcli query` | `cf-core db query` | To Migrate |
| `dbcli validate` | `cf-core db validate` | ✅ NEW (validation swarm) |

---

## 5-Phase Migration Plan

### Phase 1: Planning & Infrastructure ✅ (Weeks 1-2) - COMPLETE

**Status**: ✅ COMPLETE

**Completed**:
- [x] Migration roadmap documented (this document)
- [x] Output module consolidation plan (CF-CORE-CLI-Consolidation-Plan.md)
- [x] Validation agent swarm implemented (5,850 lines)
- [x] Flow-based orchestration working
- [x] Architecture documentation

**Evidence**:
- `VALIDATION-SWARM-EXECUTIVE-SUMMARY.md`
- `CF-CORE-CLI-Consolidation-Plan.md`
- `cf_core/validation/` module operational

---

### Phase 2: Output Module Consolidation (Weeks 3-6)

**Status**: 🔄 IN PROGRESS (Week 1 implementation ready)

**Objective**: Create unified `cf_core/cli/output.py` module

#### Week 1-2: Core Module Creation
- [ ] Create `cf_core/cli/__init__.py`
- [ ] Create `cf_core/cli/output.py` with:
  - OutputFormat enum (TABLE, JSON, JSONL, COMPACT, YAML)
  - OutputFormatter class
  - Re-exports: OutputManager, DisplayManager
  - Result monad integration
  - Helper functions (format_output, format_success, format_error)
- [ ] Add JSONL support (newline-delimited JSON)
- [ ] Write unit tests (>90% coverage target)

#### Week 3-4: dbcli Integration Prep
- [ ] Add `--format` flag to 3 high-traffic dbcli commands:
  - `bulk_list_tasks()`
  - `task_show()`
  - `task_list()`
- [ ] Refactor error handling to use OutputFormatter
- [ ] Integration tests for output formats
- [ ] Performance testing (10k+ records)

**Success Criteria**:
- ✅ Single import: `from cf_core.cli.output import OutputFormatter, OutputFormat`
- ✅ JSONL format working
- ✅ Result monad integration
- ✅ Backwards compatibility maintained

---

### Phase 3: Database Plugin Creation (Weeks 7-12)

**Status**: 📋 PLANNED

**Objective**: Migrate dbcli commands into CF_Core CLI `db` plugin

#### Week 7-8: Plugin Framework
```python
# cf_core/cli/plugins/db/__init__.py

from cf_core.cli.base_plugin import BasePlugin
from cf_core.cli.output import OutputFormatter, OutputFormat
from typer import Typer

db_app = Typer(name="db", help="Database operations")

class DatabasePlugin(BasePlugin):
    """Database operations plugin (migrated from dbcli)."""

    name = "db"
    description = "Database operations and management"
    version = "2.0.0"

    def register(self, app: Typer):
        """Register database commands."""
        app.add_typer(db_app, name="db")

@db_app.command("query")
def db_query(
    query: str,
    format: str = typer.Option("table", "--format", "-f")
):
    """Execute database query with unified output."""
    formatter = OutputFormatter(format=OutputFormat(format))

    # Use repository pattern
    result = db_repo.execute_query(query)

    # Output using Result monad integration
    formatter.output_result(result)
```

#### Week 9-10: Command Migration

**Migrate Commands in Priority Order**:

1. **High-Priority** (Week 9):
   - `task create`, `task list`, `task update`, `task delete`
   - `sprint list`, `sprint status`
   - `project list`, `project show`

2. **Medium-Priority** (Week 10):
   - `query` - Raw SQL execution
   - `status` - System health checks
   - `velocity` - Analytics recording

3. **New Commands** (Week 10):
   - `validate flow` - Validation agent swarm integration
   - `validate quick` - Quick integrity checks
   - `validate full` - Full validation with performance

#### Week 11-12: Testing & Validation

- [ ] Unit tests for all migrated commands (>80% coverage)
- [ ] Integration tests for command workflows
- [ ] Performance benchmarking (compare dbcli vs cf-core db)
- [ ] Backward compatibility validation
- [ ] User acceptance testing (internal team)

**Success Criteria**:
- ✅ All dbcli commands available via `cf-core db`
- ✅ Test coverage >80%
- ✅ Performance parity or better
- ✅ Validation swarm integrated (`cf-core db validate`)

---

### Phase 4: Legacy Wrapper & Deprecation (Weeks 13-16)

**Status**: 📋 PLANNED

**Objective**: Create dbcli wrapper with deprecation warnings

#### Week 13-14: Deprecation Wrapper

```python
# python/dbcli/app.py (modified)

import sys
from rich.console import Console
from rich.panel import Panel

console = Console()

def show_deprecation_warning():
    """Show deprecation notice."""
    console.print(
        Panel(
            "[yellow]⚠️  dbcli is deprecated[/yellow]\n\n"
            "Please migrate to the unified CF_Core CLI:\n\n"
            "  Old: dbcli task list --status active\n"
            "  New: cf-core db task list --status active\n\n"
            "dbcli will be removed in Q3 2026 (6 weeks from now).\n"
            "See: docs/DBCLI-MIGRATION-GUIDE.md",
            title="Deprecation Notice",
            border_style="yellow"
        ),
        file=sys.stderr
    )

@app.callback()
def main_callback():
    """Show deprecation warning before every command."""
    show_deprecation_warning()

# All existing commands continue working but show warning
@app.command("task")
def task_operations(...):
    """Task operations (DEPRECATED - use cf-core db task)."""
    show_deprecation_warning()

    # Internally call cf-core db command
    import subprocess
    result = subprocess.run(["cf-core", "db", "task", ...])
    sys.exit(result.returncode)
```

#### Week 15: Migration Automation

**Create Migration Helper**:

```python
# scripts/migrate_dbcli_scripts.py

"""
Automated migration helper for dbcli → cf-core db.

Scans codebase for dbcli usage and suggests replacements.
"""

import re
from pathlib import Path

MIGRATIONS = {
    r'dbcli task create': 'cf-core db task create',
    r'dbcli task list': 'cf-core db task list',
    r'dbcli sprint status': 'cf-core db sprint status',
    # ... all command mappings
}

def scan_file(file_path: Path):
    """Scan file for dbcli usage."""
    content = file_path.read_text()

    for old_pattern, new_command in MIGRATIONS.items():
        matches = re.findall(old_pattern, content)
        if matches:
            print(f"Found in {file_path}:")
            print(f"  Old: {old_pattern}")
            print(f"  New: {new_command}")
            print()

# Scan entire workspace
for script in Path().rglob("*.py"):
    scan_file(script)
```

#### Week 16: Documentation

**Create Migration Guides**:

1. **User Migration Guide** (`docs/DBCLI-MIGRATION-GUIDE.md`):
   - Command mapping table
   - Step-by-step migration instructions
   - Common patterns and examples
   - Troubleshooting

2. **Internal Training**:
   - Team training sessions
   - Internal scripts migration
   - CI/CD pipeline updates

**Success Criteria**:
- ✅ Deprecation warnings displayed on all dbcli commands
- ✅ Automated migration helper working
- ✅ Migration guides complete
- ✅ Internal team trained
- ✅ 6-week grace period begins

---

### Phase 5: Full Transition & Archive (Weeks 17-20)

**Status**: 📋 PLANNED

**Objective**: Complete migration to CF_Core CLI and archive dbcli

#### Week 17-18: Internal Migration

- [ ] Migrate all internal scripts to `cf-core db`
- [ ] Update CI/CD pipelines
- [ ] Update documentation references
- [ ] Fix any remaining dbcli calls in codebase

**Verification**:
```bash
# Search for remaining dbcli usage
grep -r "dbcli" --exclude-dir=.git --exclude-dir=archive
grep -r "import dbcli" --exclude-dir=.git
grep -r "from dbcli" --exclude-dir=.git
```

#### Week 19: Validation Period

- [ ] Monitor usage metrics (dbcli vs cf-core db)
- [ ] Collect user feedback
- [ ] Address migration blockers
- [ ] Verify 100% internal adoption

**Metrics**:
- dbcli usage: 100% → 0%
- cf-core db usage: 0% → 100%
- User satisfaction: >90%

#### Week 20: Archive & Cleanup

**Archive dbcli**:

```bash
# Move to archive
mkdir -p archive/legacy-cli/dbcli
mv python/dbcli/ archive/legacy-cli/dbcli/
mv docs/dbcli-*.md archive/legacy-cli/dbcli/docs/

# Create archive README
cat > archive/legacy-cli/dbcli/README.md << 'EOF'
# dbcli - ARCHIVED

**Archived Date**: 2026-09-15
**Reason**: Functionality migrated to CF_Core CLI
**Replacement**: cf-core db [command]

This CLI has been replaced by the unified CF_Core CLI.
All functionality is available via `cf-core db` commands.

See: docs/DBCLI-MIGRATION-GUIDE.md
EOF

# Git commit
git add archive/legacy-cli/dbcli/
git commit -m "archive(dbcli): Migrate to CF_Core CLI

All dbcli functionality has been migrated to cf-core db plugin.

- Migration completed: Q3 2026
- 6-week deprecation period: Complete
- Internal adoption: 100%
- User satisfaction: 94%

See: DBCLI-TO-CF-CORE-MIGRATION-PLAN.md
"
```

**Success Criteria**:
- ✅ dbcli archived to `archive/legacy-cli/dbcli/`
- ✅ All internal scripts migrated
- ✅ Documentation updated
- ✅ 100% team adoption
- ✅ User satisfaction >90%

---

## Integration with Validation Swarm

### Current State ✅

The validation agent swarm is **already operational** with flow-based orchestration:
- 6 specialized agents (260 integrity tests)
- Flow-based DAG orchestrator
- Comprehensive reporting
- Evidence logging

### Target Integration

**Add validation commands to CF_Core CLI**:

```bash
# Quick validation (no performance)
cf-core db validate --scope quick

# Full validation (with performance benchmarks)
cf-core db validate --scope full --performance

# Visualize validation flow
cf-core db validate --visualize

# Custom database path
cf-core db validate --db-path path/to/db.sqlite
```

**Implementation**:

```python
# cf_core/cli/plugins/db/validation.py

from cf_core.validation.flow_orchestrator import FlowOrchestrator
from cf_core.cli.output import OutputFormatter, OutputFormat

@db_app.command("validate")
def db_validate(
    scope: str = typer.Option("quick", help="Validation scope"),
    performance: bool = typer.Option(False, help="Include performance tests"),
    visualize: bool = typer.Option(False, help="Show flow graph"),
    format: str = typer.Option("table", "--format", "-f")
):
    """Run validation agent swarm."""

    if visualize:
        orchestrator = FlowOrchestrator("db/trackers.sqlite")
        print(orchestrator.visualize_flow())
        return

    config = {
        "scope": scope,
        "include_performance": performance,
        "emit_evidence": True
    }

    orchestrator = FlowOrchestrator("db/trackers.sqlite", config)
    result = orchestrator.execute_flow()

    formatter = OutputFormatter(format=OutputFormat(format))

    if result.is_success:
        report = result.value
        formatter.output_single({
            "status": report['overall_status'],
            "duration_seconds": report['duration_seconds'],
            "agents_completed": f"{report['flow_summary']['completed']}/{report['flow_summary']['total_agents']}",
            "success_rate": f"{report['validation_summary']['success_rate']:.2f}%",
            "checks": f"{report['validation_summary']['passed']}/{report['validation_summary']['total_checks']}"
        }, title="Validation Report")
    else:
        formatter.output_error(result.error)
```

---

## Success Metrics

### Phase Metrics

| Phase | Metric | Target | Current |
|-------|--------|--------|---------|
| **Phase 1** | Planning Complete | 100% | ✅ 100% |
| **Phase 2** | Output Module | Complete | 🔄 Ready |
| **Phase 3** | DB Plugin | >80% coverage | 📋 Planned |
| **Phase 4** | Deprecation Wrapper | Active | 📋 Planned |
| **Phase 5** | dbcli Archived | Complete | 📋 Planned |

### Overall Metrics

| Metric | Before | Target | Timeline |
|--------|--------|--------|----------|
| **CLI Count** | 5 CLIs | 1 PRIMARY CLI | Q3 2026 |
| **Code Size** | 12,300 lines | <8,000 lines | Q3 2026 |
| **dbcli Status** | Production | Archived | Q3 2026 |
| **User Training** | 2 hours | <30 minutes | Q2 2026 |
| **Test Coverage** | ~60% | >80% | Q2 2026 |
| **User Satisfaction** | - | >90% | Q3 2026 |

---

## Risk Assessment

### High Risk

**Risk**: User resistance to CLI change
**Mitigation**:
- 6-week deprecation warnings
- Automated migration helper
- Comprehensive training
- Backward compatibility during transition

### Medium Risk

**Risk**: Command parity gaps (missing features)
**Mitigation**:
- Thorough feature mapping
- User acceptance testing
- Iterative migration with feedback

### Low Risk

**Risk**: Performance regression
**Mitigation**:
- Performance benchmarking
- Load testing (10k+ records)
- Optimization as needed

---

## Timeline Summary

```
Q4 2025: Phase 1 Complete ✅
Q1 2026: Phase 2 - Output Module 🔄
Q2 2026: Phase 3 - DB Plugin Migration 📋
Q2 2026: Phase 4 - Deprecation Wrapper 📋
Q3 2026: Phase 5 - Archive dbcli 📋
```

**Total Duration**: 20 weeks (~5 months)
**Start Date**: Q1 2026
**Complete Date**: Q3 2026

---

## Next Steps (Immediate)

1. **Review & Approve** this migration plan
2. **Begin Phase 2**: Create `cf_core/cli/output.py` module
3. **Coordinate** with validation swarm team for `db validate` integration
4. **Prepare** internal team for upcoming CLI consolidation

---

## References

- [15-Future-Roadmap.md](docs/15-Future-Roadmap.md) - Strategic roadmap
- [CF-CORE-CLI-Consolidation-Plan.md](docs/CF-CORE-CLI-Consolidation-Plan.md) - Output consolidation
- [CF-CORE-CLI-CONSOLIDATION-ROADMAP.md](projects/P-CFWORK-DOCUMENTATION/CF-CORE-CLI-CONSOLIDATION-ROADMAP.md) - Detailed roadmap
- [VALIDATION-SWARM-EXECUTIVE-SUMMARY.md](VALIDATION-SWARM-EXECUTIVE-SUMMARY.md) - Validation system
- [02-Architecture.md](docs/02-Architecture.md) - System architecture

---

**Status**: Planning Complete ✅
**Ready For**: Phase 2 Implementation
**Priority**: 🔥 CRITICAL
**Timeline**: Q1-Q3 2026 (20 weeks)

---

*Document Created: 2025-11-17*
*Author: CF_CORE Migration Team*
*Version: 1.0*
