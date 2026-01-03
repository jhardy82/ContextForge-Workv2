---
applyTo: "terminal output*, rich output*, console output*, progress bar*, Rich library*"
description: "ContextForge Terminal Output Standard - Rich console formatting requirements for all tools"
version: "1.0"
---

# ContextForge Terminal Output Standard

**Authority**: Based on Rich library implementation in `python/run_tests.py` RichProgressManager class
**Effective Date**: 2025-09-29
**Version**: 2.0.0
**Status**: MANDATORY for all ContextForge-Work tools
**Reference Implementation**: `python/run_tests.py` RichProgressManager class (validated 2025-09-29)

## Overview

This instruction establishes the **new ContextForge-Work standard** for terminal output formatting based on the comprehensive Rich library implementation. The RichProgressManager class in `python/run_tests.py` serves as the **authoritative reference implementation** demonstrating the complete Rich library integration that is now the standard for all ContextForge-Work terminal outputs.

## Core Principles (ContextForge-Work Standard)

1. **Full Rich Library Integration**: All terminal output uses comprehensive Rich library components (Console, Progress, Panel, Table, Tree, Status, Text, Align)
2. **Enhanced Visual Hierarchy**: Multi-level structured display with Rich Tree for hierarchical steps, Rich Panel for messages, Rich Table for summaries
3. **Animated Progress Indication**: Multi-phase progress bars with emoji indicators (🔧 PREP, ⚡ EXEC, 📋 PROC) and comprehensive column layouts
4. **Professional Styling**: Enhanced panels with borders, emoji, alignment, padding, and dramatic formatting for errors/warnings/success
5. **Live Operations Tracking**: Real-time operations logging with live summary tables and color-coded status icons
6. **Evidence Preservation**: Complete operations log with bounded history and comprehensive validation status

## Required Rich Components (Full Implementation)

### 1. Enhanced Console Setup (ContextForge-Work Standard)
```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, MofNCompleteColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree
from rich.status import Status
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align

console = Console()
```

### 2. Multi-Phase Progress System (Enhanced Standard)
All operations with estimated duration ≥5 seconds MUST include enhanced progress bars with emoji phase indicators:

```python
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
    console=console,
) as progress:
    # Phase 1: Preparation
    prep_task = progress.add_task(
        description="🔧 [bold bright_blue]PREP[/bold bright_blue] Initializing components",
        total=100
    )
    # Phase 2: Execution
    exec_task = progress.add_task(
        description="⚡ [bold bright_yellow]EXEC[/bold bright_yellow] Running operations",
        total=100
    )
    # Phase 3: Processing
    proc_task = progress.add_task(
        description="📋 [bold bright_magenta]PROC[/bold bright_magenta] Generating results",
        total=100
    )
```

## Standardized Color Schemes (ContextForge-Work Enhanced)

Based on RichProgressManager implementation with enhanced visual feedback:

- **Success/High Confidence**: `bright_green` with ✅ emoji and celebration formatting (🎉)
- **Warning/Medium Confidence**: `bright_yellow` with ⚠️ emoji and enhanced panel borders
- **Error/Low Confidence**: `bright_red` with ❌ and 🚨 emoji and dramatic styling
- **Info/Neutral**: `bright_blue` with ℹ️ emoji and animated spinners
- **Steps/Hierarchy**: `cyan` with 🔧 emoji and Tree structure
- **Emphasis**: `bright_magenta` for tables and summaries

## Required Output Components (ContextForge-Work Standard)

### 1. Enhanced Status Display with Animated Spinners
```python
# Rich Status with animated spinner
status_text = Text()
status_text.append("ℹ️  ", style="bold blue")
status_text.append(message, style="bold blue")
status = Status(status_text, console=console, spinner="dots12")
```

### 2. Hierarchical Step Display with Tree Structure
```python
# Rich Tree for hierarchical steps
step_tree = Tree(f"[bold cyan]🔧 [STEP] {step}[/bold cyan]")
if message:
    step_tree.add(f"[dim cyan]{message}[/dim cyan]")
console.print(step_tree)
```

### 3. Enhanced Panel Messages with Dramatic Styling
```python
# Warning Panel
warning_content = Text()
warning_content.append("⚠️  ", style="bold yellow")
warning_content.append(message, style="yellow")
warning_panel = Panel(
    Align.center(warning_content),
    title="[bold yellow]⚠️  Warning[/bold yellow]",
    border_style="yellow",
    title_align="left",
    padding=(1, 2)
)

# Error Panel with Dramatic Formatting
error_panel = Panel(
    Align.center(error_content),
    title="[bold red]🚨 Error[/bold red]",
    border_style="red",
    padding=(1, 2)
)

# Success Panel with Celebration
success_panel = Panel(
    Align.center(success_content),
    title="[bold green]🎉 Success[/bold green]",
    border_style="green",
    padding=(1, 2)
)
```

### 4. Live Operations Summary Table
```python
summary_table = Table(
    title="Operations Summary",
    show_header=True,
    header_style="bold magenta"
)
summary_table.add_column("Type", style="cyan", no_wrap=True)
summary_table.add_column("Message", style="white")
summary_table.add_column("Status", justify="center")

# Add color-coded status icons
status_icon = "✅" if op_type == "SUCCESS" else "⚠️" if op_type == "WARN" else "❌" if op_type == "ERROR" else "ℹ️"
summary_table.add_row(op_type, message, Text(status_icon, style=color))
```

### 5. Executive Summary with Rich Components
```python
# Enhanced executive summary combining multiple Rich components
exec_panel = Panel(
    f"Starting {operation_name}\n"
    f"✓ Rich UI Integration Active\n"
    f"✓ Terminal Output Standards Compliant\n"
    f"Authority: {authority_reference}",
    title=f">>> {operation_title} <<<",
    title_align="left",
    border_style="bright_blue"
)
```

## Implementation Requirements (ContextForge-Work Standard)

### 1. RichProgressManager Integration
All tools MUST implement or use the RichProgressManager pattern:
```python
class RichProgressManager:
    def __init__(self):
        self._current_status = None
        self._live_display = None
        self._operations_log = []

    def show_status(self, message: str):
        # Rich Status with animated spinner
    def show_step(self, step: str, message: str | None = None):
        # Rich Tree hierarchical display
    def show_warning(self, message: str):
        # Rich Panel with warning styling
    def show_error(self, message: str):
        # Rich Panel with dramatic error styling
    def show_success(self, message: str):
        # Rich Panel with celebration styling
    def show_live_summary(self):
        # Rich Table operations summary
```

### 2. Multi-Phase Progress with Emoji Indicators
Operations MUST use comprehensive progress tracking:
- 🔧 **PREP**: Preparation phase with bright_blue styling
- ⚡ **EXEC**: Execution phase with bright_yellow styling
- � **PROC**: Processing phase with bright_magenta styling
- Full column layout: Spinner, Text, Bar, Progress, Count, Time

### 3. Enhanced Structured Output Flow (9 Components)
1. **Rich Panel Initialization**: Startup banner with authority reference
2. **Animated Status Updates**: Live spinners with message updates
3. **Hierarchical Step Display**: Rich Tree with nested information
4. **Multi-Phase Progress**: Comprehensive progress bars with emoji
5. **Enhanced Message Panels**: Warning/Error/Success with dramatic styling
6. **Live Operations Summary**: Real-time table with color-coded status
7. **Executive Summary Tables**: Professional metrics display
8. **Evidence Preservation**: Complete validation status with references
9. **Final Status Panel**: Clear success/failure with celebration/dramatic styling

## Compliance Requirements (ContextForge-Work Standard)

### 1. Mandatory Rich Library Integration
- **All Python tools** outputting to terminal MUST use comprehensive Rich library components
- **PowerShell tools** SHOULD implement equivalent Rich-style formatting patterns where possible
- **CLI tools** MUST provide Rich-enhanced output as the default experience
- **Legacy support**: Plain text fallback only for environments where Rich is unavailable

### 2. RichProgressManager Pattern Adoption
- **New tools**: MUST implement RichProgressManager class or equivalent
- **Existing tools**: SHOULD migrate to RichProgressManager pattern during next major update
- **Operations logging**: MUST include live summary functionality with bounded history
- **Status management**: MUST use animated Status displays for long-running operations

### 3. Quality Gate Integration
- **Validation displays**: Rich Table format with color-coded status icons
- **Evidence preservation**: Complete operations log with hash references
- **Quality scores**: Professional table display with confidence color coding
- **Error handling**: Dramatic Rich Panel styling for critical issues

### 4. Authority and References (Updated)
- **Primary Authority**: `python/run_tests.py` RichProgressManager class
- **Implementation Guide**: This instruction file serves as the official standard
- **Validation Method**: All tools implementing this standard MUST demonstrate Rich components in operation
- **Compliance Testing**: Tools MUST pass Rich component validation during QA review

## Quality Gates

Tools implementing this standard MUST:
1. ✅ Use Rich console for all terminal output
2. ✅ Include progress indicators for operations ≥5 seconds
3. ✅ Implement standardized color schemes
4. ✅ Display executive summary with key metrics
5. ✅ Show validation status and evidence references
6. ✅ Use structured output flow (9 components above)
7. ✅ Include compliance validation in tool tests

## Non-Compliance

Tools that do not implement this standard:
- MUST be flagged during code review
- SHOULD be updated to compliance during next modification
- MAY be marked as technical debt if conversion is complex

### 5. Migration Path for Existing Tools
- **High Priority**: Testing and validation tools (immediate migration required)
- **Medium Priority**: CLI utilities and development tools (migrate within 30 days)
- **Low Priority**: Administrative and maintenance scripts (migrate opportunistically)
- **Support**: Legacy tools may maintain minimal Rich integration (Panel + Table minimum)

---

**Implementation Authority**: This standard is based on the comprehensive Rich library implementation in `python/run_tests.py` RichProgressManager class, validated 2025-09-29. The RichProgressManager serves as the **definitive reference implementation** for all ContextForge-Work terminal output standards.

**Adoption Status**: ACTIVE as of 2025-09-29. All new ContextForge-Work tools MUST implement this Rich library standard. Existing tools SHOULD migrate to this standard during their next update cycle.
