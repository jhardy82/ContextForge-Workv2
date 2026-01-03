# CF_CORE CLI Consolidation Plan

**Date**: 2025-11-17
**Status**: Phase 1 - Infrastructure Discovery Complete
**Branch**: sprint-1-plugin-infrastructure

---

## Executive Summary

Workspace research revealed **existing modular CLI infrastructure** scattered across multiple locations. Instead of building from scratch, this plan **consolidates** existing components into `cf_core/cli/` for unified, standardized output formatting.

**Key Discovery**: OutputManager, DisplayManager, and planned output.py structure already exist!

---

## Existing Infrastructure

### 1. OutputManager (`src/output_manager.py`)

**Features**:
- Thread-safe singleton pattern
- JSON envelope structure: `envelope_ok()`, `envelope_error()`, `envelope_partial()`
- Deterministic JSON encoding (datetime, Decimal, UUID, dataclasses)
- Stdout emit helpers: `echo_ok()`, `echo_error()`, `echo_partial()`
- Minified JSON with `separators=(',', ':')`

**Example**:
```python
from src.output_manager import get_output_manager

mgr = get_output_manager()

# Success envelope
mgr.echo_ok({"task_id": "T-001", "status": "completed"})
# Output: {"version":"1.0.0","ok":true,"result":{...},"meta":{...}}

# Error envelope
mgr.echo_error("Task not found", code="NOT_FOUND")
# Output: {"version":"1.0.0","ok":false,"error":{...},"meta":{...}}
```

### 2. DisplayManager (`python/monitoring/display_manager.py`)

**Features**:
- Rich console with multiple display modes:
  - `DisplayMode.COMPACT` - Minimal layout
  - `DisplayMode.STANDARD` - Header + main + footer
  - `DisplayMode.DETAILED` - Events + progress + metadata
  - `DisplayMode.DASHBOARD` - Full grid with metrics
- Live display with threading
- Event tracking and buffering
- Active test monitoring with spinners
- Auto-cleanup of idle tests

**Example**:
```python
from python.monitoring.display_manager import DisplayManager, DisplayMode, DisplayConfig

config = DisplayConfig(mode=DisplayMode.STANDARD, refresh_rate=0.5)
display = DisplayManager(config)

with display:
    display.add_event(event)
    # Live Rich display updates automatically
```

### 3. Planned Output Module (Mypy Cache Signature)

**File**: `.mypy_cache/3.11/cf_core/cli/output.data.json`

**Planned Structure**:
- `OutputFormat` enum: `COMPACT`, `JSON`, `JSONL`, `TABLE`, `YAML`
- Format functions:
  - `_format_compact(data)`
  - `_format_json(data)`
  - `_format_jsonl(data)`
  - `_format_table(data, title)`
  - `_format_yaml(data)`
- Helper functions:
  - `format_output(data, format, title)`
  - `format_success(message)`
  - `format_error(message)`
  - `format_warning(message)`

---

## Gap Analysis

### What We Have ✅
1. JSON envelope structure (OutputManager)
2. Rich console display with multiple modes (DisplayManager)
3. Thread-safe singleton pattern
4. Deterministic JSON encoding
5. Event tracking and buffering
6. Planned module signature (mypy cache)

### What's Missing ❌
1. **JSONL format** (newline-delimited JSON)
2. **Unified OutputFormat enum** consolidating both managers
3. **Integration** between OutputManager and DisplayManager
4. **Location** - Components scattered, not in `cf_core/cli/`
5. **Format flag** - No standardized `--format` CLI option
6. **Result monad integration** - Error handling not connected

---

## Consolidation Strategy

### Phase 1: Create cf_core/cli/output.py (Week 1)

**Objective**: Consolidate OutputManager + DisplayManager into unified module

**Implementation**:

```python
# cf_core/cli/output.py

"""
Unified CLI Output Module

Consolidates:
- OutputManager (JSON envelopes)
- DisplayManager (Rich displays)
- JSONL support (newline-delimited JSON)
- Result monad integration
"""

from __future__ import annotations

import json
import sys
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import UTC, datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Re-export existing OutputManager for backwards compatibility
from src.output_manager import OutputManager, get_output_manager

# Re-export DisplayManager components
from python.monitoring.display_manager import (
    DisplayManager,
    DisplayMode,
    DisplayConfig,
    create_dashboard_display,
    create_compact_display
)

# Import Result monad for error handling integration
from cf_core.shared.result import Result


class OutputFormat(Enum):
    """CLI output formats."""
    TABLE = "table"          # Rich table (default, human-readable)
    JSON = "json"            # JSON envelope (OutputManager)
    JSONL = "jsonl"          # Newline-delimited JSON
    COMPACT = "compact"      # Compact display
    YAML = "yaml"            # YAML format (future)


class OutputFormatter:
    """
    Unified output formatter consolidating OutputManager and DisplayManager.

    Features:
    - JSON envelopes (from OutputManager)
    - Rich tables (from DisplayManager)
    - JSONL support (new)
    - Result monad integration (new)
    """

    def __init__(
        self,
        format: OutputFormat = OutputFormat.TABLE,
        console: Optional[Console] = None
    ):
        self.format = format
        self.console = console or Console(stderr=True)
        self.output_mgr = get_output_manager()

    def output_single(
        self,
        data: Dict[str, Any],
        title: Optional[str] = None
    ) -> None:
        """Output a single record."""
        if self.format == OutputFormat.JSON:
            # Use OutputManager envelope
            self.output_mgr.echo_ok(data)

        elif self.format == OutputFormat.JSONL:
            # JSONL: minified single-line JSON
            print(json.dumps(data, separators=(',', ':')))

        elif self.format == OutputFormat.TABLE:
            # Rich table
            table = Table(title=title or "Details")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            for key, value in data.items():
                table.add_row(key, str(value))

            self.console.print(table)

    def output_list(
        self,
        data: List[Dict[str, Any]],
        columns: List[str],
        title: Optional[str] = None
    ) -> None:
        """Output a list of records."""
        if self.format == OutputFormat.JSON:
            # Use OutputManager envelope with list
            self.output_mgr.echo_ok({"items": data, "count": len(data)})

        elif self.format == OutputFormat.JSONL:
            # JSONL: one JSON object per line
            for record in data:
                print(json.dumps(record, separators=(',', ':')))

        elif self.format == OutputFormat.TABLE:
            # Rich table
            table = Table(title=title or f"Records ({len(data)} found)")

            for col in columns:
                table.add_column(col.replace("_", " ").title())

            for record in data:
                row_data = [str(record.get(col, "")) for col in columns]
                table.add_row(*row_data)

            self.console.print(table)

    def output_error(
        self,
        error: str,
        code: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> None:
        """Output error in consistent format."""
        if self.format in (OutputFormat.JSON, OutputFormat.JSONL):
            # Use OutputManager error envelope
            self.output_mgr.echo_error(error, code=code, meta=details)
        else:
            # Rich error panel
            self.console.print(
                Panel(
                    f"[red]{error}[/red]",
                    title="❌ Error",
                    border_style="red"
                ),
                file=sys.stderr
            )

    def output_result(
        self,
        result: Result[Any],
        columns: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> None:
        """
        Output Result monad value or error.

        New feature: Direct Result<T> integration.
        """
        if result.is_failure:
            self.output_error(result.error)
            sys.exit(1)

        value = result.value

        # Handle single value vs list
        if isinstance(value, list):
            if columns:
                # Extract columns from domain entities
                data = [self._entity_to_dict(item) for item in value]
                self.output_list(data, columns, title)
            else:
                # Direct list output
                self.output_single({"items": value, "count": len(value)}, title)
        else:
            # Single entity
            data = self._entity_to_dict(value)
            self.output_single(data, title)

    def _entity_to_dict(self, entity: Any) -> Dict[str, Any]:
        """Convert domain entity to dictionary."""
        # Handle SprintEntity, TaskEntity with .model property
        if hasattr(entity, 'model'):
            return entity.model.model_dump()
        # Handle Pydantic models directly
        elif hasattr(entity, 'model_dump'):
            return entity.model_dump()
        # Handle dataclasses
        elif hasattr(entity, '__dataclass_fields__'):
            from dataclasses import asdict
            return asdict(entity)
        # Fallback: assume dict-like
        else:
            return dict(entity)


# Convenience functions matching mypy cache signature
def format_output(
    data: Any,
    format: OutputFormat = OutputFormat.TABLE,
    title: Optional[str] = None
) -> None:
    """Format and output data in specified format."""
    formatter = OutputFormatter(format=format)

    if isinstance(data, list):
        columns = list(data[0].keys()) if data and isinstance(data[0], dict) else []
        formatter.output_list(data, columns, title)
    else:
        formatter.output_single(data, title)


def format_success(message: str) -> None:
    """Format success message."""
    console = Console()
    console.print(
        Panel(
            f"[green]{message}[/green]",
            title="✅ Success",
            border_style="green"
        )
    )


def format_error(message: str) -> None:
    """Format error message."""
    formatter = OutputFormatter()
    formatter.output_error(message)


def format_warning(message: str) -> None:
    """Format warning message."""
    console = Console()
    console.print(
        Panel(
            f"[yellow]{message}[/yellow]",
            title="⚠️ Warning",
            border_style="yellow"
        )
    )


# Export all public APIs
__all__ = [
    # Enums
    "OutputFormat",
    "DisplayMode",

    # Classes
    "OutputFormatter",
    "OutputManager",
    "DisplayManager",
    "DisplayConfig",

    # Functions
    "format_output",
    "format_success",
    "format_error",
    "format_warning",
    "get_output_manager",
    "create_dashboard_display",
    "create_compact_display",
]
```

### Phase 2: Integration with CLI Commands (Week 2)

**Update tasks_cli.py**:

```python
from cf_core.cli.output import OutputFormatter, OutputFormat
from cf_core.repositories.sprint_repository import SqliteSprintRepository

@tasks_app.command("list")
def list_tasks(
    status: Optional[str] = None,
    format: str = typer.Option("table", "--format", "-f",
                               help="Output format: table|json|jsonl")
):
    """List tasks with optional status filter."""

    # Create formatter
    formatter = OutputFormatter(format=OutputFormat(format))

    # Query via repository
    repo = SqliteTaskRepository("db/tasks.db")
    result = repo.find_by_status(status) if status else repo.find_all()

    # Output using Result monad integration
    formatter.output_result(
        result,
        columns=["id", "title", "status", "priority"],
        title=f"Tasks (status={status})" if status else "All Tasks"
    )
```

### Phase 3: Testing (Week 3)

**Unit Tests** (`tests/cf_core/cli/test_output.py`):

```python
import pytest
from cf_core.cli.output import OutputFormatter, OutputFormat
from cf_core.shared.result import Result

class TestOutputFormatter:
    """Test unified output formatter."""

    def test_table_format(self, capsys):
        """Table format renders Rich table."""
        formatter = OutputFormatter(format=OutputFormat.TABLE)
        data = {"id": "T-001", "title": "Test"}

        formatter.output_single(data)

        captured = capsys.readouterr()
        assert "T-001" in captured.err

    def test_jsonl_format(self, capsys):
        """JSONL format outputs newline-delimited JSON."""
        formatter = OutputFormatter(format=OutputFormat.JSONL)
        data = [{"id": "T-001"}, {"id": "T-002"}]

        formatter.output_list(data, columns=["id"])

        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert len(lines) == 2

    def test_result_monad_success(self, capsys):
        """Result monad success outputs data."""
        formatter = OutputFormatter(format=OutputFormat.JSONL)
        result = Result.success({"id": "T-001", "title": "Test"})

        formatter.output_result(result)

        captured = capsys.readouterr()
        assert "T-001" in captured.out

    def test_result_monad_failure(self, capsys):
        """Result monad failure outputs error."""
        formatter = OutputFormatter(format=OutputFormat.JSONL)
        result = Result.failure("Task not found")

        with pytest.raises(SystemExit):
            formatter.output_result(result)

        captured = capsys.readouterr()
        assert "Task not found" in captured.err
```

---

## Benefits of Consolidation

### 1. Single Import Location ✅
```python
# Before (scattered)
from src.output_manager import get_output_manager
from python.monitoring.display_manager import DisplayManager

# After (unified)
from cf_core.cli.output import OutputFormatter, OutputFormat
```

### 2. Consistent API ✅
All CLI commands use the same pattern:
```python
formatter = OutputFormatter(format=OutputFormat(format_flag))
formatter.output_result(result, columns=[...])
```

### 3. Result Monad Integration ✅
Errors flow automatically from Repository → CLI → Output:
```python
result = repo.get_by_id("T-001")  # Returns Result<TaskEntity>
formatter.output_result(result)   # Handles success/failure
```

### 4. Backwards Compatibility ✅
Existing code continues to work:
```python
# Old code still works
from src.output_manager import get_output_manager
mgr = get_output_manager()
mgr.echo_ok(data)
```

### 5. JSONL Support ✅
New format for machine parsing:
```bash
cf-cli tasks list --format=jsonl | jq '.title'
```

---

## File Organization

### Current State
```
C:\Users\james.e.hardy\Documents\PowerShell Projects\
├── src/
│   └── output_manager.py              # JSON envelopes
├── python/
│   └── monitoring/
│       └── display_manager.py         # Rich displays
└── cf_core/
    └── cli/                           # Empty (ready)
```

### Target State (After Consolidation)
```
cf_core/
├── cli/
│   ├── __init__.py                    # Export public APIs
│   └── output.py                      # Unified module
│       ├── OutputFormat enum
│       ├── OutputFormatter class
│       ├── Re-exports: OutputManager, DisplayManager
│       └── Helper functions
├── shared/
│   └── result.py                      # Result monad
└── repositories/
    └── sprint_repository.py           # Repository pattern
```

### Migration Path

**No breaking changes** - old imports continue working:
```python
# Old code (still works)
from src.output_manager import get_output_manager

# New code (preferred)
from cf_core.cli.output import OutputFormatter, OutputFormat
```

---

## Implementation Timeline

### Week 1: Foundation
- [x] Research existing infrastructure (COMPLETE)
- [ ] Create `cf_core/cli/__init__.py`
- [ ] Create `cf_core/cli/output.py` with consolidation
- [ ] Add JSONL support
- [ ] Add Result monad integration
- [ ] Write unit tests (90%+ coverage target)

### Week 2: CLI Integration
- [ ] Add `--format` flag to `bulk_list_tasks()`
- [ ] Add `--format` flag to `task_show()`
- [ ] Add `--format` flag to `task_list()`
- [ ] Refactor error handling to use OutputFormatter
- [ ] Update command help text

### Week 3: Testing & Validation
- [ ] Integration tests for all commands
- [ ] Test JSONL piping: `cf-cli tasks list --format=jsonl | jq`
- [ ] Performance testing (10k+ records)
- [ ] Backwards compatibility verification
- [ ] Documentation updates

### Week 4: Documentation & Release
- [ ] Update `cf_core/README.md`
- [ ] Create CLI usage guide
- [ ] Add examples to command help
- [ ] Migration guide for existing scripts
- [ ] Sprint-1 completion checklist

---

## Success Criteria

✅ **Consolidation**:
- Single `cf_core/cli/output.py` module
- OutputManager and DisplayManager re-exported
- Backwards compatibility maintained

✅ **Functionality**:
- JSONL format working
- Result monad integration
- All formats (table, json, jsonl) tested

✅ **Integration**:
- At least 3 CLI commands using new formatter
- Error handling consistent across formats
- `--format` flag standardized

✅ **Quality**:
- 90%+ test coverage on new code
- All integration tests passing
- Documentation complete

---

## Next Steps

1. **Review this consolidation plan**
2. **Approve implementation approach**
3. **Begin Week 1: Create cf_core/cli/output.py**
4. **Execute in sprint-1-plugin-infrastructure branch**

**Status**: Ready for implementation
**Estimated Effort**: 4 weeks
**Risk Level**: Low (consolidating existing, tested components)

---

**Last Updated**: 2025-11-17
**Author**: Claude (Sequential Thinking Mode + Workspace Exploration)
**Branch**: sprint-1-plugin-infrastructure
