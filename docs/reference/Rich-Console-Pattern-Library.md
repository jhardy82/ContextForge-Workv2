# Rich Console Pattern Library for ContextForge

**Source Authority**: `cf_constitutional_quality_gates.py`
**Created**: 2025-09-28
**Version**: 1.0.0
**Reference**: See `.github/instructions/terminal-output.instructions.md` for compliance requirements

## Reusable Rich Console Components

### 1. Standard Console Setup
```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

console = Console()
```

### 2. Multi-Phase Progress Pattern
```python
def execute_with_progress(phases):
    """Execute multiple phases with Rich progress display"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        for phase_name, phase_func, total_steps in phases:
            task = progress.add_task(f"{phase_name}...", total=total_steps)
            result = phase_func(progress, task)
            yield result
```

### 3. Executive Summary Table Builder
```python
def create_executive_summary_table(title="Executive Summary"):
    """Create standardized executive summary table"""
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Status", style="white")
    return table

def add_confidence_row(table, label, value, thresholds=(0.8, 0.6)):
    """Add confidence row with color coding"""
    high, med = thresholds
    if value >= high:
        status_style = "bright_green"
        status_text = "✅ HIGH"
    elif value >= med:
        status_style = "bright_yellow"
        status_text = "⚠️ MEDIUM"
    else:
        status_style = "bright_red"
        status_text = "❌ LOW"

    table.add_row(
        label,
        f"{value:.1f}%",
        Text(status_text, style=status_style)
    )
```

### 4. Analysis Results Table Creator
```python
def create_analysis_table(title="Analysis Results"):
    """Create standardized analysis results table"""
    table = Table(title=title, show_header=True, header_style="bold blue")
    table.add_column("Component", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Description", style="dim")
    return table

def add_analysis_row(table, component, score, description):
    """Add analysis row with score-based status"""
    if score >= 80:
        status = Text("PASS", style="bright_green")
    elif score >= 60:
        status = Text("WARN", style="bright_yellow")
    else:
        status = Text("FAIL", style="bright_red")

    table.add_row(component, f"{score}", status, description)
```

### 5. Quality Gates Display
```python
def create_quality_gates_display(gates_data):
    """Create quality gates validation display"""
    table = Table(title="🏛️ Quality Gates Validation", show_header=True, header_style="bold magenta")
    table.add_column("Gate", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Threshold", justify="right", style="dim")

    for gate_name, score, threshold in gates_data:
        if score >= threshold:
            status = Text("PASSED", style="bright_green")
        elif score >= threshold - 10:  # Within 10% of threshold
            status = Text("WARNING", style="bright_yellow")
        else:
            status = Text("FAILED", style="bright_red")

        table.add_row(gate_name, f"{score}%", status, f"{threshold}%")

    return table
```

### 6. Critical Issues Tree
```python
def create_critical_issues_tree(issues):
    """Create critical issues tree display"""
    if not issues:
        return Panel("[green]✅ No critical issues detected[/green]",
                    title="🚨 Critical Issues", border_style="green")

    tree = Tree("🚨 [bold red]Critical Issues[/bold red]")
    for issue in issues:
        tree.add(f"[red]{issue}[/red]")

    return tree
```

### 7. Recommendations Tree
```python
def create_recommendations_tree(recommendations):
    """Create recommendations tree display"""
    if not recommendations:
        return Panel("[dim]No recommendations at this time[/dim]",
                    title="💡 Recommendations", border_style="blue")

    tree = Tree("💡 [bold green]Recommendations[/bold green]")
    for i, rec in enumerate(recommendations, 1):
        tree.add(f"[green]{i}. {rec}[/green]")

    return tree
```

### 8. Evidence Summary Panel
```python
def create_evidence_panel(evidence_data):
    """Create evidence preservation summary panel"""
    content = []

    for category, items in evidence_data.items():
        content.append(f"[bold cyan]{category}:[/bold cyan]")
        for item in items:
            content.append(f"  • {item}")
        content.append("")  # Blank line

    total_records = sum(len(items) for items in evidence_data.values())
    content.append(f"[bold]Total Evidence Records: {total_records}[/bold]")

    return Panel(
        "\n".join(content),
        title="📋 Evidence Preservation",
        title_align="left",
        border_style="blue"
    )
```

### 9. Final Status Display
```python
def display_final_status(success, message="Analysis completed"):
    """Display final operation status"""
    if success:
        console.print(f"\n✅ [bold green]{message} - PASSED[/bold green]")
    else:
        console.print(f"\n❌ [bold red]{message} - FAILED[/bold red]")
```

### 10. Spinner Context Manager
```python
from contextlib import contextmanager

@contextmanager
def spinner_context(description):
    """Context manager for operations with spinner"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(description, total=None)
        yield progress, task
```

## Complete Implementation Template

```python
class ContextForgeRichTool:
    """Template class implementing ContextForge Rich console standard"""

    def __init__(self):
        self.console = Console()

    def execute_analysis(self):
        """Execute analysis with full Rich console implementation"""
        # 1. Multi-phase progress
        phases = [
            ("Initialization", self._initialize, 10),
            ("Core Analysis", self._analyze, 50),
            ("Validation", self._validate, 20),
            ("Report Generation", self._generate_report, 20)
        ]

        results = list(self.execute_with_progress(phases))

        # 2. Executive summary
        summary_table = self.create_executive_summary()
        self.console.print(summary_table)

        # 3. Analysis results
        analysis_table = self.create_analysis_results()
        self.console.print(analysis_table)

        # 4. Quality gates
        gates_display = self.create_quality_gates()
        self.console.print(gates_display)

        # 5. Critical issues
        issues_tree = self.create_critical_issues()
        self.console.print(issues_tree)

        # 6. Recommendations
        rec_tree = self.create_recommendations()
        self.console.print(rec_tree)

        # 7. Evidence summary
        evidence_panel = self.create_evidence_summary()
        self.console.print(evidence_panel)

        # 8. Final status
        self.display_final_status(success=True)

        return results
```

## Color Scheme Reference

### Standard Colors (from authority)
- **Success/High**: `bright_green` (≥80%)
- **Warning/Medium**: `bright_yellow` (60-79%)
- **Error/Low**: `bright_red` (<60%)
- **Info**: `bright_blue`
- **Emphasis**: `bright_magenta`
- **Neutral**: `white`
- **Dim**: `dim`
- **Cyan**: `cyan` (for labels/headers)

### Status Indicators
- ✅ `bright_green` - Success/Pass/High confidence
- ⚠️ `bright_yellow` - Warning/Medium confidence
- ❌ `bright_red` - Error/Fail/Low confidence
- 🔄 `bright_blue` - In progress/Info
- 📋 `bright_blue` - Information/Documentation

## Integration Checklist

- [ ] Import Rich console components
- [ ] Implement multi-phase progress for operations ≥5 seconds
- [ ] Create executive summary table with color-coded metrics
- [ ] Add analysis results with score-based status
- [ ] Include quality gates validation display
- [ ] Show critical issues in tree format
- [ ] Display recommendations as numbered tree
- [ ] Add evidence preservation summary panel
- [ ] Include final status with clear success/failure
- [ ] Use standardized color scheme throughout
- [ ] Test output with various terminal configurations
- [ ] Validate compliance with `.github/instructions/terminal-output.instructions.md`

## Usage Examples

### Basic Implementation
```python
from rich.console import Console

console = Console()
with console.status("Processing..."):
    # Do work
    pass
console.print("✅ [green]Completed successfully[/green]")
```

### Advanced Implementation
```python
# See python/rich_console_example.py for complete working example
# that demonstrates all patterns in this library
```

---

**Reference Implementation**: `python/rich_console_example.py` demonstrates all patterns in this library with working code that can be executed to see the complete ContextForge terminal output standard in action.
