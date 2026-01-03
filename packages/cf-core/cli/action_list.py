
import asyncio
import json
from functools import wraps
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from cf_core.cli.state import state
from cf_core.repositories.action_list_repository import ActionListRepository
from cf_core.services.action_list_service import ActionListService

action_list_app = typer.Typer(name="action-list", help="Manage Action Lists")
console = Console()


def async_command(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


async def _get_service_context():
    """Create service and session context."""
    session_maker = state.action_list_session_maker
    session = session_maker()
    repository = ActionListRepository(session)
    service = ActionListService(repository)
    return service, session


@action_list_app.command("list")
@async_command
async def list_action_lists(
    project_id: str | None = typer.Option(None, help="Filter by project ID"),
    sprint_id: str | None = typer.Option(None, help="Filter by sprint ID"),
    status: str | None = typer.Option(None, help="Filter by status"),
    limit: int = typer.Option(20, help="Limit results"),
):
    """List action lists."""
    service, session = await _get_service_context()
    async with session:
        result = await service.list_action_lists(
            project_id=project_id, sprint_id=sprint_id, status=status, limit=limit
        )

        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        lists, total = result.value
        table = Table(title=f"Action Lists ({total} total)")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Project", style="blue")
        table.add_column("Items", justify="right")

        for al in lists:
            table.add_row(
                al.id,
                al.name,
                al.status,
                al.project_id or "-",
                str(len(al.items)),
            )

        console.print(table)


@action_list_app.command("create")
@async_command
async def create_action_list(
    name: str = typer.Argument(..., help="Name of the action list"),
    description: str = typer.Option("", help="Description"),
    project_id: str | None = typer.Option(None, help="Project ID"),
    priority: str | None = typer.Option(None, help="Priority"),
):
    """Create a new action list."""
    service, session = await _get_service_context()
    async with session:
        result = await service.create_action_list(
            name=name,
            description=description,
            project_id=project_id,
            priority=priority,
        )

        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        al = result.value
        console.print(f"[green]Created Action List: {al.id}[/green]")
        console.print(json.dumps(al.model_dump(), indent=2, default=str))


@action_list_app.command("get")
@async_command
async def get_action_list(
    list_id: str = typer.Argument(..., help="Action List ID"),
):
    """Get details of an action list."""
    service, session = await _get_service_context()
    async with session:
        result = await service.get_action_list(list_id)

        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        al = result.value
        if not al:
            console.print(f"[red]Action List not found: {list_id}[/red]")
            raise typer.Exit(1)

        console.print(json.dumps(al.model_dump(), indent=2, default=str))


@action_list_app.command("update")
@async_command
async def update_action_list(
    list_id: str = typer.Argument(..., help="Action List ID"),
    name: str | None = typer.Option(None, help="New name"),
    status: str | None = typer.Option(None, help="New status"),
    description: str | None = typer.Option(None, help="New description"),
):
    """Update an action list."""
    service, session = await _get_service_context()
    async with session:
        updates = {}
        if name:
            updates["name"] = name
        if status:
            updates["status"] = status
        if description:
            updates["description"] = description

        if not updates:
            console.print("[yellow]No updates provided.[/yellow]")
            return

        result = await service.update_action_list(list_id, **updates)

        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        al = result.value
        console.print(f"[green]Updated Action List: {al.id}[/green]")


@action_list_app.command("delete")
@async_command
async def delete_action_list(
    list_id: str = typer.Argument(..., help="Action List ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Force delete without confirmation"),
):
    """Delete an action list."""
    if not force:
        typer.confirm(f"Are you sure you want to delete {list_id}?", abort=True)

    service, session = await _get_service_context()
    async with session:
        result = await service.delete_action_list(list_id)

        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Deleted Action List: {list_id}[/green]")


@action_list_app.command("items-add")
@async_command
async def items_add(
    list_id: str = typer.Argument(..., help="Action List ID"),
    text: str = typer.Argument(..., help="Item text"),
):
    """Add a checklist item to an action list."""
    service, session = await _get_service_context()
    async with session:
        # Get current list
        get_result = await service.get_action_list(list_id)
        if get_result.is_failure or not get_result.value:
            console.print(f"[red]Action List not found: {list_id}[/red]")
            raise typer.Exit(1)

        al = get_result.value
        new_item = {"text": text, "completed": False}
        updated_items = al.items + [new_item]

        result = await service.update_action_list(list_id, items=updated_items)
        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Added item to {list_id}[/green]")


@action_list_app.command("items-toggle")
@async_command
async def items_toggle(
    list_id: str = typer.Argument(..., help="Action List ID"),
    index: int = typer.Argument(..., help="Item index (0-based)"),
):
    """Toggle completion status of a checklist item."""
    service, session = await _get_service_context()
    async with session:
        get_result = await service.get_action_list(list_id)
        if get_result.is_failure or not get_result.value:
            console.print(f"[red]Action List not found: {list_id}[/red]")
            raise typer.Exit(1)

        al = get_result.value
        if index < 0 or index >= len(al.items):
            console.print(f"[red]Index out of bounds. List has {len(al.items)} items.[/red]")
            raise typer.Exit(1)

        # Clone items to modify
        import copy
        updated_items = copy.deepcopy(al.items)
        updated_items[index]["completed"] = not updated_items[index].get("completed", False)

        result = await service.update_action_list(list_id, items=updated_items)
        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        status = "completed" if updated_items[index]["completed"] else "pending"
        console.print(f"[green]Item {index} toggled to {status}[/green]")


@action_list_app.command("items-remove")
@async_command
async def items_remove(
    list_id: str = typer.Argument(..., help="Action List ID"),
    index: int = typer.Argument(..., help="Item index (0-based)"),
):
    """Remove a checklist item."""
    service, session = await _get_service_context()
    async with session:
        get_result = await service.get_action_list(list_id)
        if get_result.is_failure or not get_result.value:
            console.print(f"[red]Action List not found: {list_id}[/red]")
            raise typer.Exit(1)

        al = get_result.value
        if index < 0 or index >= len(al.items):
            console.print(f"[red]Index out of bounds. List has {len(al.items)} items.[/red]")
            raise typer.Exit(1)

        updated_items = [item for i, item in enumerate(al.items) if i != index]

        result = await service.update_action_list(list_id, items=updated_items)
        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Item {index} removed from {list_id}[/green]")


@action_list_app.command("task-add")
@async_command
async def task_add(
    list_id: str = typer.Argument(..., help="Action List ID"),
    task_id: str = typer.Argument(..., help="Task ID to add"),
):
    """Add a task reference to an action list."""
    service, session = await _get_service_context()
    async with session:
        result = await service.add_task_to_action_list(list_id, task_id)
        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]Task {task_id} added to {list_id}[/green]")


@action_list_app.command("task-remove")
@async_command
async def task_remove(
    list_id: str = typer.Argument(..., help="Action List ID"),
    task_id: str = typer.Argument(..., help="Task ID to remove"),
):
    """Remove a task reference from an action list."""
    service, session = await _get_service_context()
    async with session:
        result = await service.remove_task_from_action_list(list_id, task_id)
        if result.is_failure:
            console.print(f"[red]Error: {result.error}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]Task {task_id} removed from {list_id}[/green]")
