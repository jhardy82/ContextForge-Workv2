---
applyTo: "terminal output*, rich output*, console output*, progress bar*, Rich library*"
description: "ContextForge Terminal Output Standard - Rich console formatting"
---

# Terminal Output Quick Reference

## Required Imports

```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

console = Console()
```

## Progress Bars (≥5 sec operations)

```python
with Progress(SpinnerColumn(), BarColumn(), console=console) as progress:
    task = progress.add_task("🔧 Processing...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
```

## Panels

```python
# Success
console.print(Panel("Done!", title="✅ Success", border_style="green"))

# Error
console.print(Panel(str(error), title="❌ Error", border_style="red"))

# Warning
console.print(Panel(msg, title="⚠️ Warning", border_style="yellow"))
```

## Color Scheme

| Type | Color | Emoji |
|------|-------|-------|
| Success | `bright_green` | ✅ 🎉 |
| Warning | `bright_yellow` | ⚠️ |
| Error | `bright_red` | ❌ 🚨 |
| Info | `bright_blue` | ℹ️ |
| Step | `cyan` | 🔧 |

## Full Reference
See `.github/instructions/archive/terminal-output-full.md`
