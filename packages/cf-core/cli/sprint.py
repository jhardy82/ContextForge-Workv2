"""Sprint Management CLI Commands.

Handles create, list, update, and show operations for Sprints.
"""

from __future__ import annotations

from datetime import datetime

import typer

from cf_core.cli.output import get_output
from cf_core.cli.state import state

# Create the Typer app for the 'sprint' command group
sprint_app = typer.Typer(
    help="Manage Sprints (Time-boxed iterations)",
    no_args_is_help=True,
)


@sprint_app.command("list")
def list_sprints(
    project_id: str | None = typer.Option(
        None, "--project", "-p", help="Filter by project"
    ),
    active_only: bool = typer.Option(
        False, "--active", "-a", help="Show only active sprints"
    ),
    limit: int = typer.Option(50, "--limit", "-l", help="Max number of sprints"),
):
    """List sprints."""
    out = get_output()

    result = state.service.list_sprints(
        project_id=project_id,
        active_only=active_only,
        limit=limit,
    )

    if result.is_failure:
        out.error(f"Failed to list sprints: {result.error}")
        raise typer.Exit(code=1)

    sprints = result.value
    if state.settings.machine_mode:
        out.json({
            "success": True,
            "data": {"sprints": [s.to_dict() for s in sprints], "total": len(sprints)}
        })
    elif not sprints:
        out.info("No sprints found.")
    else:
        out.print(f"[bold]Found {len(sprints)} sprint(s):[/bold]")
        for sprint in sprints:
            status = getattr(sprint, "status", "unknown")
            is_active = sprint.is_active() if hasattr(sprint, "is_active") else False
            icon = "🏃" if is_active else "📋"
            out.print(f"  {icon} {sprint.id}: {sprint.name} ({status})")


@sprint_app.command("create")
def create_sprint(
    name: str = typer.Argument(..., help="Sprint Name"),
    start_date: str = typer.Argument(..., help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Argument(..., help="End date (YYYY-MM-DD)"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Sprint goal/description"
    ),
    project_id: str | None = typer.Option(
        None, "--project", "-p", help="Associated project ID"
    ),
):
    """Create a new sprint."""
    out = get_output()

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        out.error(f"Invalid date format: {e}")
        raise typer.Exit(code=1)

    result = state.service.create_sprint(
        name=name,
        start_date=start,
        end_date=end,
        description=description or "",
        project_id=project_id,
    )

    if result.is_failure:
        out.error(f"Failed to create sprint: {result.error}")
        raise typer.Exit(code=1)

    if state.settings.machine_mode:
        out.json({"success": True, "data": {"id": result.value.id}})
    else:
        out.success(f"Sprint created: {result.value.id}")


@sprint_app.command("show")
def show_sprint(
    sprint_id: str = typer.Argument(..., help="Sprint ID"),
):
    """Show details for a specific sprint."""
    out = get_output()

    result = state.service.get_sprint(sprint_id)
    if result.is_failure:
        out.error(f"Sprint not found: {sprint_id}")
        raise typer.Exit(code=1)

    sprint = result.value
    if state.settings.machine_mode:
        out.json(sprint.to_dict())
    else:
        out.print(f"[bold]Sprint: {sprint.id}[/bold]")
        out.print(f"  Name:        {sprint.name}")
        out.print(f"  Status:      {getattr(sprint, 'status', 'N/A')}")
        out.print(f"  Start:       {sprint.start_date}")
        out.print(f"  End:         {sprint.end_date}")
        if hasattr(sprint, "description") and sprint.description:
            out.print(f"  Description: {sprint.description}")
        if hasattr(sprint, "project_id") and sprint.project_id:
            out.print(f"  Project:     {sprint.project_id}")


@sprint_app.command("update")
def update_sprint(
    sprint_id: str = typer.Argument(..., help="Sprint ID"),
    name: str | None = typer.Option(None, help="New Name"),
    status: str | None = typer.Option(None, help="New Status"),
    start_date: str | None = typer.Option(None, help="New Start (YYYY-MM-DD)"),
    end_date: str | None = typer.Option(None, help="New End (YYYY-MM-DD)"),
    description: str | None = typer.Option(None, help="New Description"),
):
    """Update an existing sprint."""
    out = get_output()

    # Parse dates if provided
    start = None
    end = None
    try:
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        out.error(f"Invalid date format: {e}")
        raise typer.Exit(code=1)

    result = state.service.update_sprint(
        sprint_id=sprint_id,
        name=name,
        status=status,
        start_date=start,
        end_date=end,
        description=description,
    )

    if result.is_failure:
        out.error(f"Failed to update sprint: {result.error}")
        raise typer.Exit(code=1)

    if state.settings.machine_mode:
        out.json({"success": True, "data": {"id": sprint_id}})
    else:
        out.success(f"Sprint updated: {sprint_id}")

    # Explicit success exit for machine mode consistency
    raise typer.Exit(code=0)


@sprint_app.command("current")
def current_sprint(
    project_id: str | None = typer.Option(None, "--project", "-p", help="Filter by project"),
):
    """Show the currently active sprint."""
    out = get_output()

    result = state.service.list_sprints(
        project_id=project_id,
        active_only=True,
        limit=1,
    )

    if result.is_failure:
        out.error(f"Failed to get current sprint: {result.error}")
        raise typer.Exit(code=1)

    sprints = result.value
    if not sprints:
        out.info("No active sprint found.")
        raise typer.Exit(code=0)

    sprint = sprints[0]
    if state.settings.machine_mode:
        out.json(sprint.to_dict())
    else:
        out.print(f"[bold green]Current Sprint: {sprint.id}[/bold green]")
        out.print(f"  Name: {sprint.name}")
        out.print(f"  Ends: {sprint.end_date}")

    # Explicit success exit for machine mode consistency
    raise typer.Exit(code=0)
