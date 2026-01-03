"""ContextForge CLI Package.

Provides the unified command-line interface for ContextForge task management.

Architecture:
    - Typer-based CLI with noun-verb command pattern
    - Universal --machine flag for agent consumption
    - Structured JSON output in machine mode
    - Semantic exit codes (BSD/POSIX conventions)

Command Pattern:
    cf <resource> <action> [options]

Examples:
    cf task list
    cf task create "My Task" --priority high
    cf sprint start "Sprint 1"
    cf project status --machine

Usage:
    from cf_core.cli import app, run_cli

    # Run the CLI
    run_cli()

    # Or access the Typer app directly
    app(["task", "list"])
"""

from cf_core.cli.main import app, run_cli

__all__ = ["app", "run_cli"]
