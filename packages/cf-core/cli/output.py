"""ContextForge CLI Output Adapter.

Provides dual-output capability:
- Human-readable Rich terminal output
- Machine-readable JSONL session logging

This module bridges the gap between cf_core.cli and python.terminal.enhanced_console,
ensuring all CLI output is both beautiful for humans AND traceable for AI agents.

Usage:
    from cf_core.cli.output import get_output, Output, output_success, output_error

    out = get_output()
    out.success("Task created", task_id="T-001")
    out.table("Tasks", tasks, ["id", "title", "status"])
    out.json({"status": "ok"})  # For machine mode

    # Or use helper functions for consistent exit codes:
    output_success({"tasks": tasks})  # Exits with code 0
    output_error("VALIDATION_ERROR", "Invalid input")  # Exits with code 1

Session logs are written to: logs/cli_session_<timestamp>.log
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from pydantic import BaseModel, Field

# Lazy import for performance - EnhancedTerminalConsole only when needed
if TYPE_CHECKING:
    from src.terminal.enhanced_console import EnhancedTerminalConsole


# Module-level singleton
_output_instance: Output | None = None


class Output:
    """Unified CLI output with dual human/machine support.

    Wraps EnhancedTerminalConsole to provide:
    - Rich terminal output for humans
    - JSONL session logging for AI agents
    - Machine mode bypass for pure JSON output

    The session log captures ALL output for:
    - AI agent consumption
    - Audit trails
    - Debugging complex workflows
    """

    def __init__(
        self,
        machine_mode: bool | None = None,
        log_session: bool = True,
    ) -> None:
        """Initialize output adapter."""

        from cf_core.config.settings import get_settings

        cfg = get_settings()

        self.machine_mode = machine_mode if machine_mode is not None else cfg.machine_mode
        self.log_session = log_session

        # Session metadata
        self.session_id = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        self.session_start = datetime.now(UTC)

        # Session log path - priority: settings.output.session_log_path > default
        if cfg.output.session_log_path:
            self.session_log_path = Path(cfg.output.session_log_path)
            self.session_log_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            self.session_log_path = log_dir / f"cli_session_{self.session_id}.log"

        # Configure UnifiedLogger to use the SAME session log path
        from cf_core.logging import configure_logging

        configure_logging(log_path=self.session_log_path)

        # Create EnhancedTerminalConsole (lazy import to avoid circular deps)
        self._console: EnhancedTerminalConsole | None = None

        # Log session start
        if self.log_session:
            self._log_event(
                "session_start",
                {
                    "session_id": self.session_id,
                    "machine_mode": self.machine_mode,
                    "python_version": sys.version,
                    "platform": sys.platform,
                },
            )

    @property
    def console(self) -> EnhancedTerminalConsole:
        """Lazy-load EnhancedTerminalConsole."""
        if self._console is None:
            # Import here to avoid circular dependencies
            from src.terminal.enhanced_console import EnhancedTerminalConsole

            self._console = EnhancedTerminalConsole(
                log_session=self.log_session,
                session_log_file=str(self.session_log_path),
            )
        return self._console

    def _log_event(self, event_type: str, data: Any) -> None:
        """Write event to session log (JSONL format)."""
        if not self.log_session:
            return

        # Align with UnifiedLogger schema for test compatibility
        # Every event must have timestamp, action, and ok
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "session_id": self.session_id,
            "action": event_type,
            "ok": True,  # Default to True for high-level lifecycle events
        }

        # Flatten data into top-level for compatibility with find_events/assert_event_schema
        if isinstance(data, dict):
            entry.update(data)
        else:
            entry["data"] = data

        with open(self.session_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    # =========================================================================
    # Human-Readable Output (Rich)
    # =========================================================================

    def print(self, *args, **kwargs) -> None:
        """Print to terminal (Rich-formatted) and log to session."""
        if self.machine_mode:
            # In machine mode, convert to plain text
            message = " ".join(str(arg) for arg in args)
            print(message, file=sys.stderr)
        else:
            self.console.print(*args, **kwargs)

        # Always log
        self._log_event("print", {"message": " ".join(str(a) for a in args)})

    def success(self, message: str, **details) -> None:
        """Print success message with green checkmark."""
        if self.machine_mode:
            self.json({"status": "success", "message": message, **details})
        else:
            self.console.success(message, **details)

        self._log_event("success", {"message": message, **details})

    def error(self, message: str, **details) -> None:
        """Print error message with red X."""
        if self.machine_mode:
            self.json({"status": "error", "message": message, **details})
        else:
            self.console.error(message, **details)

        self._log_event("error", {"message": message, **details})

    def warning(self, message: str, **details) -> None:
        """Print warning message with yellow triangle."""
        if self.machine_mode:
            self.json({"status": "warning", "message": message, **details})
        else:
            self.console.warning(message, **details)

        self._log_event("warning", {"message": message, **details})

    def info(self, message: str, **details) -> None:
        """Print info message with blue info icon."""
        if self.machine_mode:
            self.json({"status": "info", "message": message, **details})
        else:
            self.console.info(message, **details)

        self._log_event("info", {"message": message, **details})

    def table(
        self,
        title: str,
        data: list[dict[str, Any]],
        columns: list[str] | None = None,
    ) -> None:
        """Print data as a Rich table."""
        if not data:
            self.info(f"No {title.lower()} found.")
            return

        if self.machine_mode:
            self.json({"title": title, "data": data, "count": len(data)})
        else:
            self.console.status_table(title, data, columns)

        self._log_event("table", {"title": title, "row_count": len(data)})

    def panel(self, content: str, title: str | None = None, style: str = "blue") -> None:
        """Print content in a Rich panel."""
        if self.machine_mode:
            self.json({"title": title, "content": content})
        else:
            self.console.panel(content, title, style)

        self._log_event("panel", {"title": title, "content_length": len(content)})

    def markdown(self, content: str) -> None:
        """Render markdown content."""
        if self.machine_mode:
            # Strip markdown for machine mode
            print(content, file=sys.stderr)
        else:
            self.console.markdown(content)

        self._log_event("markdown", {"content_length": len(content)})

    # =========================================================================
    # Machine-Readable Output (JSON)
    # =========================================================================

    def json(self, data: Any, title: str | None = None) -> None:
        """Output JSON (always to stdout for machine consumption)."""
        if isinstance(data, str):
            output = data
        else:
            output = json.dumps(data, indent=2, default=str)

        # JSON always goes to stdout (for piping)
        print(output)

        self._log_event("json_output", {"data": data, "title": title})

    def jsonl(self, data: list[dict[str, Any]]) -> None:
        """Output JSON Lines (one object per line)."""
        for item in data:
            print(json.dumps(item, default=str))

        self._log_event("jsonl_output", {"record_count": len(data)})

    # =========================================================================
    # Progress and Status
    # =========================================================================

    def progress(self, description: str = "Working..."):
        """Return a progress context manager."""
        return self.console.progress_context(description)

    def status(self, message: str):
        """Show a status spinner."""
        return self.console.console.status(message)

    # =========================================================================
    # Session Management
    # =========================================================================

    def close(self) -> None:
        """Close session and finalize logs."""
        duration = (datetime.now(UTC) - self.session_start).total_seconds()

        # Log session summary first (baseline requirement)
        self._log_event(
            "session_summary",
            {
                "session_id": self.session_id,
                "duration_seconds": duration,
                "status": "success",
            },
        )

        self._log_event(
            "session_end",
            {
                "session_id": self.session_id,
                "duration_seconds": duration,
            },
        )

        if self._console:
            self._console.close_session()


def get_output(
    machine_mode: bool | None = None,
    force_new: bool = False,
) -> Output:
    """Get or create the global Output instance.

    Args:
        machine_mode: Override machine mode setting
        force_new: Force creation of a new instance

    Returns:
        Global Output instance
    """
    global _output_instance

    if _output_instance is None or force_new:
        _output_instance = Output(machine_mode=machine_mode)

    return _output_instance


def set_machine_mode(enabled: bool) -> None:
    """Set machine mode on the global output instance."""
    out = get_output()
    out.machine_mode = enabled
    out._log_event("mode_change", {"machine_mode": enabled})


# =========================================================================
# Helper for Task Display
# =========================================================================


def display_task_list(
    out: Output,
    tasks: list[dict[str, Any]],
    settings_machine_mode: bool,
    verbose: bool = False,
    filters: dict[str, Any] | None = None,
) -> None:
    """Display task list in appropriate format.

    Args:
        out: Output instance
        tasks: List of task dictionaries
        settings_machine_mode: Whether machine mode is enabled
        verbose: Show verbose output
        filters: Applied filters (for verbose mode)
    """
    if settings_machine_mode:
        out.json({"success": True, "data": {"tasks": tasks, "total": len(tasks)}})
    elif not tasks:
        out.info("No tasks found.")
    else:
        out.print(f"[bold]Found {len(tasks)} task(s):[/bold]")
        for task in tasks:
            status = task.get("status", "unknown")
            status_icon = "●" if status == "in_progress" else "○"
            priority = task.get("priority", "medium")
            priority_color = {
                "critical": "red",
                "high": "yellow",
                "medium": "blue",
                "low": "dim",
            }.get(priority, "white")

            out.print(
                f"  {status_icon} [{priority_color}]{task['id']}[/]: {task['title']} [{status}]"
            )

        if verbose and filters:
            filter_str = ", ".join(f"{k}={v}" for k, v in filters.items() if v)
            out.print(f"\n[dim]Filters: {filter_str}[/dim]")


def display_task_detail(
    out: Output,
    task: dict[str, Any],
    settings_machine_mode: bool,
) -> None:
    """Display single task details.

    Args:
        out: Output instance
        task: Task dictionary
        settings_machine_mode: Whether machine mode is enabled
    """
    if settings_machine_mode:
        out.json(task)
    else:
        out.print(f"[bold]Task: {task['id']}[/bold]")
        out.print(f"  Title:    {task.get('title', 'N/A')}")
        out.print(f"  Status:   {task.get('status', 'N/A')}")
        out.print(f"  Priority: {task.get('priority', 'N/A')}")

        if task.get("description"):
            raw_desc = task.get("description", "")
            desc = raw_desc[:100] + "..." if len(raw_desc) > 100 else raw_desc
            out.print(f"  Description: {desc}")
        if task.get("assignee"):
            out.print(f"  Assignee: {task['assignee']}")
        if task.get("sprint_id"):
            out.print(f"  Sprint:   {task['sprint_id']}")
        if task.get("project_id"):
            out.print(f"  Project:  {task['project_id']}")
        if task.get("tags"):
            out.print(f"  Tags:     {', '.join(task['tags'])}")


# =============================================================================
# CLI Response Model (Pydantic)
# =============================================================================

class CLIResponse(BaseModel):
    """Standardized CLI response model for JSON schema validation.

    Ensures consistent structure for machine-readable output.
    All CLI commands should return responses conforming to this model.
    """

    success: bool = Field(..., description="Whether the operation succeeded")
    data: dict[str, Any] | None = Field(None, description="Response data payload")
    error: str | None = Field(None, description="Error message if success=False")
    error_type: str | None = Field(None, description="Error type/code for categorization")


def output_success(data: dict[str, Any]) -> None:
    """Output success response and exit with code 0.

    Args:
        data: Response data to output

    Raises:
        typer.Exit: Always exits with code 0
    """
    response = CLIResponse(success=True, data=data)
    out = get_output()
    out.json(response.model_dump())
    raise typer.Exit(code=0)


def output_error(error_type: str, message: str) -> None:
    """Output error response and exit with code 1.

    Args:
        error_type: Error category/code (e.g., "VALIDATION_ERROR", "NOT_FOUND")
        message: Human-readable error message

    Raises:
        typer.Exit: Always exits with code 1
    """
    response = CLIResponse(success=False, error=message, error_type=error_type)
    out = get_output()
    out.json(response.model_dump())
    raise typer.Exit(code=1)


# Convenience exports
__all__ = [
    "Output",
    "get_output",
    "set_machine_mode",
    "display_task_list",
    "display_task_detail",
    "display_project_list",
    "display_project_detail",
    "CLIResponse",
    "output_success",
    "output_error",
]


def display_project_list(
    out: Output,
    projects: list[dict[str, Any]],
    settings_machine_mode: bool,
    verbose: bool = False,
    filters: dict[str, Any] | None = None,
) -> None:
    """Display project list in appropriate format."""
    if settings_machine_mode:
        out.json({"projects": projects, "total": len(projects)})
    elif not projects:
        out.info("No projects found.")
    else:
        out.print(f"[bold]Found {len(projects)} project(s):[/bold]")
        for project in projects:
            status = project.get("status", "unknown")
            color = "green" if status == "active" else "dim"
            owner = project.get('owner', 'Unassigned')
            out.print(
                f"  [{color}]{project['id']}[/]: {project['name']} "
                f"({status}) - {owner}"
            )

        if verbose and filters:
            filter_str = ", ".join(f"{k}={v}" for k, v in filters.items() if v)
            out.print(f"\n[dim]Filters: {filter_str}[/dim]")


def display_project_detail(
    out: Output,
    project: dict[str, Any],
    settings_machine_mode: bool,
) -> None:
    """Display single project details."""
    if settings_machine_mode:
        out.json(project)
    else:
        out.print(f"[bold]Project: {project['id']}[/bold]")
        out.print(f"  Name:        {project.get('name', 'N/A')}")
        out.print(f"  Status:      {project.get('status', 'N/A')}")
        out.print(f"  Owner:       {project.get('owner', 'N/A')}")

        if project.get("description"):
            out.print(f"  Description: {project['description']}")

        if project.get("start_date") or project.get("target_end_date"):
            start = project.get("start_date", "N/A")
            end = project.get("target_end_date", "N/A")
            out.print(f"  Timeline:    {start} -> {end}")

        if project.get("tags"):
            out.print(f"  Tags:        {', '.join(project['tags'])}")

        if project.get("team_members"):
            out.print(f"  Team:        {', '.join(project['team_members'])}")
