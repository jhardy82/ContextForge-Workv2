"""
Context CLI module for ContextForge.
Handles context hierarchy, templates, and resolution using the new DAO layer.
"""

from __future__ import annotations

import asyncio
import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cf_core.cli.state import state
from cf_core.config.settings import get_settings
from cf_core.dao.context import ContextModel, ContextRepository

app = typer.Typer(name="context", help="Context hierarchy management", no_args_is_help=True)
console = Console()


# Dependency Helper
async def get_repo(ctx: typer.Context) -> ContextRepository:
    """Get ContextRepository from Typer context or create new for one-off."""
    # Ideally ctx.obj has the session or container.
    # For now, if not present, we create a fresh connection (similar to legacy behavior)
    # But strictly we should use the Session managed by main.py if possible.
    # Given main.py setup might be complex, we'll do a quick safe fallback:

    if ctx.obj and "db_session" in ctx.obj:
        return ContextRepository(ctx.obj["db_session"])

    # Use centralized state session factory
    session = await state.get_db_session()
    return ContextRepository(session)


@app.command()
def create(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Context name (unique)"),
    parent: str | None = typer.Option(None, "--parent", "-p", help="Parent context name"),
    context_type: str = typer.Option("generic", "--type", "-t", help="Context type"),
    description: str = typer.Option(None, "--description", "-d"),
    attributes: str = typer.Option(None, "--attributes", "-a", help="Attributes as JSON"),
):
    """Create a new context."""

    async def _run():
        repo = await get_repo(ctx)
        try:
            attrs = json.loads(attributes) if attributes else {}

            # Dimensions mapping (simplified)
            # In real usage we might want to map specific keys to dim_ columns
            # For now, we put everything known into attributes or specific dims if match

            new_ctx = await repo.create(
                kind=context_type,
                title=name,
                summary=description,
                dim_operational=json.dumps(attrs)
                if attrs
                else None,  # Storing generic attrs in operational for now or expand logic
            )

            if parent:
                parent_node = await repo.get_by_title_or_id(parent)
                if parent_node:
                    # Edge: Child (new) -> Parent (existing)
                    # "related_to"
                    await repo.create_edge(new_ctx.id, parent_node.id, "related_to")
                else:
                    console.print(
                        f"[yellow]Parent '{parent}' not found. Created context without parent.[/yellow]"
                    )

            await repo.commit()
            console.print(f"[green]Context '{name}' created.[/green] ID: {new_ctx.id}")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            # await repo.session.rollback()
        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                await repo.session.close()

    asyncio.run(_run())


@app.command("list")
def list_contexts(
    ctx: typer.Context,
    kind: str | None = typer.Option(None, "--type", "-t", help="Filter by type"),
    limit: int = typer.Option(20, "--limit", "-l"),
):
    """List contexts."""

    async def _run():
        repo = await get_repo(ctx)
        try:
            items = await repo.list_by_kind(kind, limit)
            table = Table(title="Contexts")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Kind", style="magenta")
            table.add_column("Title", style="green")

            for item in items:
                table.add_row(str(item.id), item.kind, item.title)

            console.print(table)
        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                await repo.session.close()

    asyncio.run(_run())


@app.command()
def tree(ctx: typer.Context, root: str | None = typer.Argument(None, help="Root ID/Name")):
    """Visualize context tree."""

    async def _run():
        repo = await get_repo(ctx)
        try:
            root_id = None
            if root:
                node = await repo.get_by_title_or_id(root)
                if node:
                    root_id = node.id
                else:
                    console.print(f"[red]Root '{root}' not found.[/red]")
                    return

            nodes = await repo.get_context_tree(root_id)
            if not nodes:
                console.print("[yellow]No contexts.[/yellow]")
                return

            # Build Tree
            # Nodes have: id, title, kind, depth, path
            # Strategy: Map ID -> Tree Node.
            # Iterate: Since CTE returns parents then children (if BFS), or mixed?
            # CTE usually recurses down.
            # We can use the 'path' array to determine hierarchy.

            root_tree = Tree("Contexts")
            id_map = {}

            # If explicit root
            if root_id:
                # The first item is usually the root in this CTE logic?
                # Actually verify CTE output order.
                pass

            # Generic approach:
            # 1. Create Tree nodes for everyone
            # 2. Attach to parents

            # With `path` array: [RootID, ChildID, GrandChildID]
            # Parent of X is path[-2] if len(path) > 1

            # First pass: Create all tree objects
            for n in nodes:
                label = f"[bold cyan]{n['title']}[/bold cyan] ({n['kind']})"
                id_map[n["id"]] = Tree(label)

            # Second pass: Link
            for n in nodes:
                current_id = n["id"]
                path = n["path"]
                # path is list of UUIDs

                current_node_obj = id_map[current_id]

                if len(path) > 1:
                    parent_id = path[-2]
                    if parent_id in id_map:
                        id_map[parent_id].add(current_node_obj)
                    else:
                        # Parent outside of result set? Attach to root_tree
                        root_tree.add(current_node_obj)
                else:
                    # It's a root in this view
                    root_tree.add(current_node_obj)

            console.print(root_tree)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                await repo.session.close()

    asyncio.run(_run())


@app.command()
def get(
    ctx: typer.Context,
    identifier: str = typer.Argument(..., help="ID or Title"),
    resolve: bool = typer.Option(False, "--resolve", "-r"),
):
    """Get context details."""

    async def _run():
        repo = await get_repo(ctx)
        try:
            target = await repo.get_by_title_or_id(identifier)
            if not target:
                console.print(f"[red]Not found: {identifier}[/red]")
                return

            if resolve:
                data = await repo.resolve_context(target.id)
                console.print(
                    Panel(json.dumps(str(data), indent=2), title=f"Resolved: {target.title}")
                )
            else:
                # Raw
                console.print(
                    Panel(
                        f"Title: {target.title}\nKind: {target.kind}\nID: {target.id}",
                        title="Context",
                    )
                )

        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                await repo.session.close()

    asyncio.run(_run())
