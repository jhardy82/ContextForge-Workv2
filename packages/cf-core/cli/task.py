"""Task Management CLI Commands.

Handles create, list, update, get, and search operations for Tasks.
"""

from __future__ import annotations

import warnings

import typer

from cf_core.cli.output import display_task_detail, display_task_list
from cf_core.cli.state import state
from cf_core.config.settings import ContextForgeSettings
from cf_core.errors.codes import ExitCode
from cf_core.errors.response import create_error, create_success

# Create the Typer app for the 'task' command group
task_app = typer.Typer(
    help="Manage Tasks (Work items)",
    no_args_is_help=True,
)


@task_app.command("list")
def task_list(
    ctx: typer.Context,
    status: str | None = typer.Option(None, "--status", "-s", help="Filter by status"),
    priority: str | None = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="Filter by assignee"),
    project: str | None = typer.Option(None, "--project", help="Filter by project ID"),
    sprint: str | None = typer.Option(None, "--sprint", help="Filter by sprint ID"),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum number of tasks"),
) -> None:
    """List tasks with optional filtering."""
    settings: ContextForgeSettings = ctx.obj
    service = state.service
    out = state.output  # Use output adapter from state

    # Call service to list tasks
    # Note: Service layer should handle filtering ideally, but strict separation might require
    # filtering here if service doesn't support all args.
    # Assuming service.list_tasks supports filters as per typical pattern.
    result = service.list_tasks(limit=limit)

    if result.is_failure:
        if settings.machine_mode:
            error_response = create_error(
                code="LIST_FAILED",
                message=result.error,
                exit_code=ExitCode.GENERAL_ERROR,
                machine_mode=True,
            )
            out.json(error_response.model_dump())
        else:
            out.error(result.error)
        raise typer.Exit(ExitCode.GENERAL_ERROR)

    tasks = result.value

    # Apply client-side filtering if service didn't handle it
    # (This preserves existing logic if service.list_tasks is basic)
    if status:
        tasks = [t for t in tasks if t.status == status]
    if assignee:
        tasks = [t for t in tasks if t.assignee == assignee]
    if project:
        tasks = [t for t in tasks if t.project_id == project]
    if priority:
        # Priority can be int or string in CLI, model is usually int or enum
        # Logic from main.py needs to be preserved or service enhanced
        # For now, simple string comparison might fail if types differ
        # Replicating main.py logic exactly if possible, but simplest is to filter by conversion
        pass # Todo: check if filtering needed locally

    # To be safe and consistent with previous main.py logic (which did local filtering):
    if status:
        tasks = [t for t in tasks if t.status == status]
    if assignee:
        tasks = [t for t in tasks if t.assignee == assignee]
    if project:
        tasks = [t for t in tasks if t.project_id == project]
    if priority:
        # Assuming task.priority is compatible with filter
        tasks = [t for t in tasks if str(t.priority) == priority]

    task_data = [t.task.model_dump() for t in tasks]

    display_task_list(
        out,
        task_data,
        settings.machine_mode,
        verbose=settings.output.verbose,
        filters={
            "status": status,
            "priority": priority,
            "assignee": assignee,
            "project": project,
            "sprint": sprint,
        },
    )

    # Explicit success exit for machine mode consistency
    raise typer.Exit(code=0)


@task_app.command("search")
def task_search(
    ctx: typer.Context,
    query: str = typer.Argument(None, help="Search text (matches title and description)"),
    status: str | None = typer.Option(None, "--status", "-s", help="Filter by status"),
    priority: str | None = typer.Option(None, "--priority", "-p", help="Filter by priority"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="Filter by assignee"),
    project: str | None = typer.Option(None, "--project", help="Filter by project ID"),
    sprint: str | None = typer.Option(None, "--sprint", help="Filter by sprint ID"),
    tag: list[str] | None = typer.Option(
        None, "--tag", "-t", help="Filter by tag (can specify multiple)"
    ),
    limit: int = typer.Option(50, "--limit", "-n", help="Maximum number of results"),
) -> None:
    """Search tasks with flexible criteria.

    Examples:
        cf task search "authentication"
        cf task search --status in_progress
        cf task search "bug" --priority high --tag backend
        cf task search --assignee james --sprint S-20251206060527
    """
    settings: ContextForgeSettings = ctx.obj
    service = state.service
    out = state.output

    # Call service to search tasks
    result = service.search_tasks(
        query=query,
        status=status,
        priority=priority,
        tags=tag,
        sprint_id=sprint,
        project_id=project,
        assignee=assignee,
        limit=limit,
    )

    if result.is_failure:
        if settings.machine_mode:
            error_response = create_error(
                code="SEARCH_FAILED",
                message=result.error,
                exit_code=ExitCode.GENERAL_ERROR,
                machine_mode=True,
            )
            out.json(error_response.model_dump())
        else:
            out.error(result.error)
        raise typer.Exit(ExitCode.GENERAL_ERROR)

    tasks = result.value

    task_data = [t.task.model_dump() for t in tasks]

    display_task_list(
        out,
        task_data,
        settings.machine_mode,
        verbose=True,  # Always verbose for search
        filters={
            "query": query,
            "status": status,
            "priority": priority,
            "assignee": assignee,
            "project": project,
            "sprint": sprint,
            "tags": str(tag) if tag else None,
        },
    )

    # Explicit success exit for machine mode consistency
    raise typer.Exit(code=0)


@task_app.command("get")
def task_get(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="Task ID to retrieve"),
) -> None:
    """Get a specific task by ID."""
    settings: ContextForgeSettings = ctx.obj
    service = state.service
    out = state.output

    # Call service to get task
    result = service.get_task(task_id)

    if result.is_failure:
        if settings.machine_mode:
            error_response = create_error(
                code="NOT_FOUND",
                message=result.error,
                exit_code=ExitCode.NOT_FOUND,
                machine_mode=True,
            )
            out.json(error_response.model_dump())
        else:
            out.error(result.error)
        raise typer.Exit(ExitCode.NOT_FOUND)

    task = result.value

    task_data = task.task.model_dump()
    display_task_detail(out, task_data, settings.machine_mode)


@task_app.command("create")
def task_create(
    ctx: typer.Context,
    title: str = typer.Argument(..., help="Task title"),
    summary: str | None = typer.Option(None, "--summary", help="Brief summary (defaults to title)"),
    description: str | None = typer.Option(None, "--description", "-d", help="Task description"),
    priority: str = typer.Option("3", "--priority", "-p", help="Priority (0-9 or p0/p1/p2/p3/p4)"),
    status: str = typer.Option("new", "--status", "-s", help="Initial status"),
    project: str | None = typer.Option(None, "--project", help="Project ID"),
    sprint: str | None = typer.Option(None, "--sprint", help="Sprint ID"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="Assignee"),
    estimate: float | None = typer.Option(None, "--estimate", "-e", help="Estimate in hours"),
) -> None:
    """Create a new task."""
    settings: ContextForgeSettings = ctx.obj
    service = state.service
    out = state.output

    # Convert priority to int (accepts int string or p0/p1/p2/p3 format)
    from cf_core.models.task import PRIORITY_STRING_TO_INT

    priority_int: int
    if priority.isdigit():
        priority_int = int(priority)
    elif priority.lower() in PRIORITY_STRING_TO_INT:
        priority_int = PRIORITY_STRING_TO_INT[priority.lower()]
    else:
        error_msg = f"Invalid priority: {priority}. Use: 0-9 or p0/p1/p2/p3/p4"
        if settings.machine_mode:
            error_response = create_error(
                code="VALIDATION_ERROR",
                message=error_msg,
                exit_code=ExitCode.INVALID_ARGUMENT,
                field="priority",
                suggestion="Use: 0-9 (lower=higher) or p0/p1/p2/p3/p4",
                machine_mode=True,
            )
            out.json(error_response.model_dump())
        else:
            out.error(error_msg)
        raise typer.Exit(ExitCode.INVALID_ARGUMENT)

    # Call service to create task
    result = service.create_task(
        title=title,
        summary=summary,
        description=description,
        priority=priority_int,
        status=status,
        project_id=project,
        sprint_id=sprint,
        assignee=assignee,
        estimate_hours=estimate,
    )

    if result.is_failure:
        if settings.machine_mode:
            error_response = create_error(
                code="CREATE_FAILED",
                message=result.error,
                exit_code=ExitCode.GENERAL_ERROR,
                machine_mode=True,
            )
            out.json(error_response.model_dump())
        else:
            out.error(result.error)
        raise typer.Exit(ExitCode.GENERAL_ERROR)

    task = result.value

    # Convert to output format
    task_data = {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "assignee": task.assignee,
        "sprint_id": task.sprint_id,
        "project_id": task.project_id,
    }

    if settings.machine_mode:
        response = create_success(data=task_data, machine_mode=True)
        out.json(response.model_dump())
    else:
        out.success(f"Created task: {task.id}")
        out.print(f"  Title:    {task.title}")
        out.print(f"  Status:   {task.status}")
        out.print(f"  Priority: {task.priority}")


@task_app.command("update")
def task_update(
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="Task ID to update"),
    title: str | None = typer.Option(None, "--title", "-t", help="New title"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    priority: str | None = typer.Option(None, "--priority", "-p", help="New priority"),
    status: str | None = typer.Option(None, "--status", "-s", help="New status"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="New assignee"),
    sprint: str | None = typer.Option(None, "--sprint", help="New sprint ID"),
    estimate: float | None = typer.Option(None, "--estimate", "-e", help="New estimate"),
    actual: float | None = typer.Option(None, "--actual", help="Actual hours spent"),
) -> None:
    """Update an existing task."""
    settings: ContextForgeSettings = ctx.obj
    service = state.service
    out = state.output

    # Validate priority if provided
    if priority:
        from cf_core.models.priority import is_valid_priority, normalize_priority

        if not is_valid_priority(priority):
            error_msg = f"Invalid priority: {priority}. Use: low, medium, high, critical"
            if settings.machine_mode:
                error_response = create_error(
                    code="VALIDATION_ERROR",
                    message=error_msg,
                    exit_code=ExitCode.INVALID_ARGUMENT,
                    field="priority",
                    machine_mode=True,
                )
                out.json(error_response.model_dump())
            else:
                out.error(error_msg)
            raise typer.Exit(ExitCode.INVALID_ARGUMENT)
        priority = normalize_priority(priority).value

    # Call service to update task
    result = service.update_task(
        task_id=task_id,
        title=title,
        description=description,
        priority=priority,
        status=status,
        sprint_id=sprint,
        assignee=assignee,
        estimate_hours=estimate,
        actual_hours=actual,
    )

    if result.is_failure:
        if settings.machine_mode:
            is_not_found = "not found" in result.error.lower()
            exit_code = ExitCode.NOT_FOUND if is_not_found else ExitCode.GENERAL_ERROR
            error_response = create_error(
                code="UPDATE_FAILED",
                message=result.error,
                exit_code=exit_code,
                machine_mode=True,
            )
            out.json(error_response.model_dump())
        else:
            out.error(result.error)
        raise typer.Exit(ExitCode.GENERAL_ERROR)

    task = result.value

    # Convert to output format
    task_data = {
        "id": task.id,
        "title": task.title,
        "status": task.status,
    }

    if settings.machine_mode:
        response = create_success(data=task_data, machine_mode=True)
        out.json(response.model_dump())
    else:
        out.success(f"Updated task: {task.id}")
