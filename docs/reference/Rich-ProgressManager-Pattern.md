# RichProgressManager Pattern - ContextForge-Work Standard

**Version**: 2.0.0
**Effective Date**: 2025-09-29
**Authority**: `python/run_tests.py` RichProgressManager class
**Status**: MANDATORY for all ContextForge-Work tools

## Overview

The RichProgressManager pattern is the official ContextForge-Work standard for terminal output, providing comprehensive Rich library integration with professional visual enhancement and live operations tracking.

## Core Architecture

### Class Structure
```python
class RichProgressManager:
    """Enhanced progress manager using only Rich library components for consistent UX."""

    def __init__(self):
        self._current_status = None
        self._live_display = None
        self._operations_log = []  # Bounded history tracking
```

### Required Rich Components
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

## Core Methods

### 1. Status Display with Animated Spinners
```python
def show_status(self, message: str):
    """Display status with Rich Status spinner and enhanced formatting."""
    # Create enhanced status with spinner
    status_text = Text()
    status_text.append("ℹ️  ", style="bold blue")
    status_text.append(message, style="bold blue")

    self._current_status = Status(status_text, console=console, spinner="dots12")
    self._current_status.start()

    # Log for operations tracking
    self._operations_log.append(("INFO", message, "blue"))
```

### 2. Hierarchical Step Display with Tree Structure
```python
def show_step(self, step: str, message: str | None = None):
    """Display step with Rich Tree structure and enhanced formatting."""
    # Create step tree for better hierarchy
    step_tree = Tree(f"[bold cyan]🔧 [STEP] {step}[/bold cyan]")
    if message:
        step_tree.add(f"[dim cyan]{message}[/dim cyan]")

    console.print(step_tree)
    self._operations_log.append(("STEP", full_message, "cyan"))
```

### 3. Enhanced Panel Messages with Dramatic Styling
```python
def show_warning(self, message: str):
    """Display warning with Rich panel and enhanced formatting."""
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
    console.print(warning_panel)

def show_error(self, message: str):
    """Display error with Rich panel and dramatic formatting."""
    error_panel = Panel(
        Align.center(error_content),
        title="[bold red]🚨 Error[/bold red]",
        border_style="red",
        padding=(1, 2)
    )

def show_success(self, message: str):
    """Display success with Rich panel and celebration formatting."""
    success_panel = Panel(
        Align.center(success_content),
        title="[bold green]🎉 Success[/bold green]",
        border_style="green",
        padding=(1, 2)
    )
```

### 4. Live Operations Summary Table
```python
def show_live_summary(self):
    """Display live summary of operations using Rich Live display."""
    summary_table = Table(
        title="Operations Summary",
        show_header=True,
        header_style="bold magenta"
    )
    summary_table.add_column("Type", style="cyan", no_wrap=True)
    summary_table.add_column("Message", style="white")
    summary_table.add_column("Status", justify="center")

    for op_type, message, color in self._operations_log[-5:]:  # Show last 5
        status_icon = "✅" if op_type == "SUCCESS" else "⚠️" if op_type == "WARN" else "❌" if op_type == "ERROR" else "ℹ️"
        summary_table.add_row(op_type, message, Text(status_icon, style=color))
```

## Multi-Phase Progress System

### Progress Implementation
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

## Color Schemes and Visual Standards

### Enhanced Color Mapping
- **Success**: `bright_green` with ✅ and 🎉 emoji
- **Warning**: `bright_yellow` with ⚠️ emoji
- **Error**: `bright_red` with ❌ and 🚨 emoji
- **Info**: `bright_blue` with ℹ️ emoji
- **Steps**: `cyan` with 🔧 emoji
- **Emphasis**: `bright_magenta` for tables

### Emoji Phase Indicators
- 🔧 **PREP**: Preparation phase (bright_blue)
- ⚡ **EXEC**: Execution phase (bright_yellow)
- 📋 **PROC**: Processing phase (bright_magenta)

## Implementation Pattern

### 1. Initialization
```python
# Initialize Rich console and progress manager
console = Console()
progress_mgr = RichProgressManager()

# Show startup banner
init_panel = Panel(
    f"Starting {operation_name}\n"
    f"✓ Rich UI Integration Active\n"
    f"✓ Terminal Output Standards Compliant\n"
    f"Authority: python/run_tests.py RichProgressManager",
    title=f">>> {operation_title} <<<",
    title_align="left",
    border_style="bright_blue"
)
console.print(init_panel)
```

### 2. Operation Execution
```python
# Status updates with spinners
progress_mgr.show_status("Initializing Rich components")

# Hierarchical steps
progress_mgr.show_step("Phase 1: Setup", "Configuring environment")
progress_mgr.show_step("Phase 2: Execution", "Running operations")

# Result handling
if success:
    progress_mgr.show_success("Operation completed successfully")
else:
    progress_mgr.show_error("Operation failed with errors")
```

### 3. Cleanup and Summary
```python
# Show operations summary
progress_mgr.show_live_summary()

# Cleanup resources
progress_mgr.cleanup()
```

## Compliance Requirements

### Mandatory Features
1. ✅ **RichProgressManager class** or equivalent implementation
2. ✅ **Animated Status displays** with spinners for long operations
3. ✅ **Rich Panel components** with proper styling and borders
4. ✅ **Rich Tree structures** for hierarchical information
5. ✅ **Rich Table summaries** with color-coded status icons
6. ✅ **Operations logging** with bounded history (last 5)
7. ✅ **Multi-phase progress** with emoji indicators
8. ✅ **Professional styling** with celebration/dramatic formatting

### Migration Priority
- **High Priority**: Testing and validation tools (immediate)
- **Medium Priority**: CLI utilities (within 30 days)
- **Low Priority**: Administrative scripts (opportunistic)

## Validation Checklist

- [ ] RichProgressManager pattern implemented
- [ ] All required Rich components imported
- [ ] Animated spinners for status updates
- [ ] Enhanced panels with borders and emoji
- [ ] Tree structures for hierarchical display
- [ ] Operations summary table functionality
- [ ] Multi-phase progress with emoji indicators
- [ ] Professional color schemes applied
- [ ] Cleanup functionality implemented
- [ ] Authority reference included in output

## Reference Implementation

The complete reference implementation is available in:
- **File**: `python/run_tests.py`
- **Class**: `RichProgressManager` (lines 70-185)
- **Validation**: Confirmed working 2025-09-29
- **Features**: All ContextForge-Work standard components

---

**Authority**: This pattern is the official ContextForge-Work standard based on the validated RichProgressManager implementation. All terminal output tools MUST implement this pattern or provide equivalent Rich library integration.
