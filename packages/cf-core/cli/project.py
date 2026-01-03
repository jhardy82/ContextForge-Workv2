"""Project Management CLI Commands.

Handles create, list, update, and show operations for Projects.
"""

from __future__ import annotations


import typer

from cf_core.cli.output import (
    display_project_detail,
    display_project_list,
    get_output,
)
from cf_core.cli.state import state

# Create the Typer app for the 'project' command group
project_app = typer.Typer(
    help="Manage Projects (Contexts for Tasks)",
    no_args_is_help=True,
)


@project_app.command("list")
def list_projects(
    status: str | None = typer.Option(None, "--status", "-s", help="Filter by status"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Filter by owner"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max number of projects"),
):
    """List projects."""
    out = get_output()

    result = state.service.list_projects(
        status=status,
        owner=owner,
        limit=limit,
    )

    if result.is_failure:
        out.error(f"Failed to list projects: {result.error}")
        raise typer.Exit(code=1)

    projects = [p.to_dict() for p in result.value]
    display_project_list(
        out,
        projects,
        settings_machine_mode=state.settings.machine_mode,
        filters={"status": status, "owner": owner},
    )


@project_app.command("create")
def create_project(
    name: str = typer.Argument(..., help="Project Name"),
    description: str | None = typer.Option(None, "--description", "-d", help="Project Description"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Project Owner"),
    tags: list[str] | None = typer.Option(None, "--tag", "-t", help="Tags"),
):
    """Create a new project."""
    out = get_output()

    result = state.service.create_project(
        name=name,
        description=description,
        owner=owner,
        tags=tags,
    )

    if result.is_failure:
        out.error(f"Failed to create project: {result.error}")
        raise typer.Exit(code=1)

    out.success(f"Project created: {result.value.id}")
    display_project_detail(
        out,
        result.value.to_dict(),
        settings_machine_mode=state.settings.machine_mode,
    )


@project_app.command("show")
def show_project(
    project_id: str = typer.Argument(..., help="Project ID"),
):
    """Show details for a specific project."""
    out = get_output()

    result = state.service.get_project(project_id)
    if result.is_failure:
        out.error(f"Project not found: {project_id}")
        raise typer.Exit(code=1)

    display_project_detail(
        out,
        result.value.to_dict(),
        settings_machine_mode=state.settings.machine_mode,
    )


@project_app.command("update")
def update_project(
    project_id: str = typer.Argument(..., help="Project ID"),
    name: str | None = typer.Option(None, help="New Name"),
    status: str | None = typer.Option(None, help="New Status"),
    description: str | None = typer.Option(None, help="New Description"),
    owner: str | None = typer.Option(None, help="New Owner"),
    tags: list[str] | None = typer.Option(
        None, "--tag", "-t", help="New Tags (replaces list if provided)"
    ),
):
    """Update an existing project."""
    out = get_output()

    result = state.service.update_project(
        project_id=project_id,
        name=name,
        status=status,
        description=description,
        owner=owner,
        tags=tags,
    )

    if result.is_failure:
        out.error(f"Failed to update project: {result.error}")
        raise typer.Exit(code=1)

    out.success(f"Project updated: {project_id}")
    display_project_detail(
        out,
        result.value.to_dict(),
        settings_machine_mode=state.settings.machine_mode,
    )
