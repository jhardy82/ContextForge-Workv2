"""Logs CLI Plugin.

Provides commands for inspecting and managing logs.
Replaces legacy plugin_logs.py.
"""
import json
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax

from cf_core.config.settings import get_settings

app = typer.Typer(
    name="logs",
    help="View and manage application logs.",
    no_args_is_help=True,
)
console = Console()

@app.command()
def tail(
    lines: int = typer.Option(20, "-n", "--lines", help="Number of lines to show."),
    follow: bool = typer.Option(False, "-f", "--follow", help="Follow log output."),
):
    """Show the last N lines of the log file and optionally follow it."""
    settings = get_settings()
    log_path = settings.logging.file

    if not log_path or not log_path.exists():
        console.print(f"[yellow]No log file found at:[/yellow] {log_path or 'Not configured'}")
        console.print("Ensure 'CONTEXTFORGE_LOG_FILE' is set or configured in config.toml.")
        raise typer.Exit(1)

    console.print(f"[dim]Reading logs from: {log_path}[/dim]")

    try:
        # Initial read
        with open(log_path, encoding="utf-8") as f:
            # Efficiently read last N lines (simple approach for now)
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]
            for line in last_lines:
                _print_log_line(line)

            if follow:
                f.seek(0, 2) # Go to end
                try:
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.1)
                            continue
                        _print_log_line(line)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Stopped following logs.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error reading logs:[/red] {e}")


def _print_log_line(line: str):
    """Pretty print a log line (JSON or Text)."""
    line = line.strip()
    if not line:
        return

    try:
        # Try to parse as JSON
        data = json.loads(line)
        # Simplified pretty print
        timestamp = data.get("timestamp", "")
        level = data.get("level", "INFO")
        message = data.get("message", "")
        # Colorize level
        level_style = "green"
        if level in ("WARNING", "WARN"): level_style = "yellow"
        elif level in ("ERROR", "CRITICAL"): level_style = "red"

        console.print(f"[{level_style}]{level}[/{level_style}] [dim]{timestamp}[/dim] {message}")
    except json.JSONDecodeError:
        # Plain text
        console.print(line)

@app.command()
def path():
    """Print the configured log file path."""
    settings = get_settings()
    if settings.logging.file:
        console.print(str(settings.logging.file))
    else:
        console.print("[yellow]Log file not configured.[/yellow]")
