import asyncio
import os
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from cf_core.cli.state import state
from cf_core.config.settings import get_settings
from cf_core.dao.qse import QSERepository
from cf_core.services.qse import QSEService

app = typer.Typer(name="qse", help="Quantum Sync Engine logic.", no_args_is_help=True)
console = Console()


async def get_service(ctx: typer.Context) -> QSEService:
    """Get QSEService with repo injection."""
    if ctx.obj and "db_session" in ctx.obj:
        repo = QSERepository(ctx.obj["db_session"])
        return QSEService(repo)

    session = await state.get_db_session()
    repo = QSERepository(session)
    return QSEService(repo)


@app.command()
def collect(
    ctx: typer.Context,
    target: str = typer.Argument(..., help="File path or command to collect evidence from"),
    type: str = typer.Option("file", "--type", "-t", help="Type of evidence: file or command"),
    task_id: str = typer.Option(None, "--task", help="Associated Task ID"),
    session_id: str = typer.Option(None, "--session", help="Associated Session ID"),
    api_url: str = typer.Option(
        None, "--api", help="API URL to push evidence to (overrides local DB)"
    ),
):
    """Collect evidence (file hash or command output)."""

    async def _run():
        # Check env var if api_url not provided
        nonlocal api_url
        if not api_url:
            api_url = os.environ.get("CONTEXTFORGE_API_URL")

        if api_url:
            # API Push Mode
            import requests

            payload = {
                "artifact_type": type,
                "task_id": task_id,
                "session_id": session_id,
                "metadata_": {"collected_via": "cli_push"},
            }

            try:
                if type == "file":
                    # Calculate hash locally for the payload
                    from cf_core.services.qse import QSEService

                    if not os.path.exists(target):
                        console.print(f"[red]File not found: {target}[/red]")
                        return
                    abs_path = os.path.abspath(target)
                    payload["artifact_hash"] = QSEService._calculate_file_hash(abs_path)
                    payload["file_size_bytes"] = os.path.getsize(abs_path)
                    payload["artifact_path"] = abs_path

                elif type == "command":
                    # Run command locally, capture output
                    import hashlib
                    import subprocess

                    # ... reuse command logic or duplicate?
                    # Ideally we refactor `collect_command_evidence` to separate collection from storage,
                    # but for now we implement the collection logic here for API mode.
                    proc = subprocess.run(target, shell=True, capture_output=True, text=True)
                    output = proc.stdout + proc.stderr
                    payload["artifact_hash"] = hashlib.sha256(output.encode("utf-8")).hexdigest()
                    payload["file_size_bytes"] = len(output)
                    payload["metadata_"]["command"] = target
                    payload["metadata_"]["exit_code"] = proc.returncode
                    payload["metadata_"]["output_preview"] = output[:200]

                # Push to API
                endpoint = f"{api_url.rstrip('/')}/qse/evidence"
                console.print(f"Pushing evidence to {endpoint}...")
                resp = requests.post(endpoint, json=payload, timeout=10)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    console.print(f"[green]Evidence Pushed:[/green] {data.get('id')}")
                    console.print(f"Hash: {data.get('artifact_hash')}")
                else:
                    console.print(f"[red]API Error {resp.status_code}:[/red] {resp.text}")

            except Exception as e:
                console.print(f"[red]API Push Failed:[/red] {e}")
            return

        # Local Mode (Existing Logic)
        service = await get_service(ctx)
        try:
            if type == "file":
                ev = await service.collect_file_evidence(target, task_id, session_id)
                console.print(f"[green]Evidence Collected:[/green] {ev.id}")
                console.print(f"Hash: {ev.artifact_hash}")
            elif type == "command":
                ev = await service.collect_command_evidence(target, task_id, session_id)
                console.print(f"[green]Command Evidence Collected:[/green] {ev.id}")
                console.print(f"Output Hash: {ev.artifact_hash}")
                if ev.metadata_:
                    console.print(f"Exit Code: {ev.metadata_.get('exit_code')}")
            else:
                console.print(f"[red]Unknown type: {type}[/red]")

            await service.repo.commit()

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                await service.repo.session.close()

    asyncio.run(_run())


@app.command()
def gates(
    ctx: typer.Context,
    list_all: bool = typer.Option(False, "--all", "-a", help="List all gates (including disabled)"),
):
    """List defined quality gates."""

    async def _run():
        service = await get_service(ctx)
        try:
            gates = await service.repo.list_gates(enabled_only=not list_all)

            table = Table(title="Quality Gates")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Type")
            table.add_column("Threshold")
            table.add_column("Enabled", justify="center")

            for g in gates:
                thresh = (
                    f"{g.threshold_operator} {g.threshold_value}"
                    if g.threshold_value is not None
                    else "N/A"
                )
                table.add_row(g.id, g.name, g.gate_type, thresh, "Yes" if g.enabled else "No")

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                await service.repo.session.close()

    asyncio.run(_run())


@app.command()
def evaluate(
    ctx: typer.Context,
    gate_name: str = typer.Argument(..., help="Name of the gate to evaluate"),
    value: float = typer.Argument(..., help="Current value to check against threshold"),
    task_id: str = typer.Option(None, "--task", help="Associated Task ID"),
):
    """Evaluate a quality gate."""

    async def _run():
        service = await get_service(ctx)
        try:
            eval_res = await service.evaluate_gate(gate_name, value, task_id)
            await service.repo.commit()

            color = "green" if eval_res.passed else "red"
            status = "PASSED" if eval_res.passed else "FAILED"

            console.print(f"Gate '{gate_name}' evaluation: [{color}]{status}[/{color}]")
            console.print(f"Actual: {eval_res.actual_value}")
            console.print(f"Evaluation ID: {eval_res.id}")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                await service.repo.session.close()

    asyncio.run(_run())


@app.command()
def create_gate(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Gate name"),
    gate_type: str = typer.Option("custom", "--type", "-t", help="Gate type"),
    threshold: float = typer.Option(0.0, "--threshold", help="Threshold value"),
    operator: str = typer.Option(
        ">=", "--operator", "-o", help="Threshold operator (>=, <=, =, >, <, !=)"
    ),
    severity: str = typer.Option("error", "--severity", help="Severity level"),
    description: str = typer.Option(None, "--desc", help="Gate description"),
):
    """Create a new quality gate."""

    async def _run():
        service = await get_service(ctx)
        try:
            gate = await service.repo.create_gate(
                id=f"GATE-{name.upper().replace(' ', '_')}",
                name=name,
                gate_type=gate_type,
                threshold_value=threshold,
                threshold_operator=operator,
                severity=severity,
                description=description,
            )
            await service.repo.commit()
            console.print(f"[green]Gate Created:[/green] {gate.id}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        finally:
            if not (ctx.obj and "db_session" in ctx.obj):
                if hasattr(service.repo, "session"):
                    await service.repo.session.close()
                    if hasattr(service.repo.session, "bind") and service.repo.session.bind:
                        await service.repo.session.bind.dispose()

    asyncio.run(_run())


@app.command()
def init_db(
    ctx: typer.Context,
    force: bool = typer.Option(
        False, "--force", help="Force re-creation of tables (CRITICAL: DATA LOSS)"
    ),
):
    """Initialize QSE database schema."""

    async def _run():
        settings = get_settings()
        url = settings.database.url.get_secret_value()
        if "sqlite" in url:
            if "aiosqlite" not in url:
                url = url.replace("sqlite://", "sqlite+aiosqlite://")
        else:
            url = url.replace("postgresql://", "postgresql+asyncpg://")

        from cf_core.dao.base import Base  # Ensure Base is imported
        from cf_core.dao.qse import (
            QSEComplianceChecklistModel,
            QSEEvidenceModel,
            QSEGateEvaluationModel,
            QSEQualityGateModel,
            QSESessionModel,
        )

        qse_tables = [
            QSEEvidenceModel.__table__,
            QSEQualityGateModel.__table__,
            QSEGateEvaluationModel.__table__,
            QSESessionModel.__table__,
            QSEComplianceChecklistModel.__table__,
        ]

        engine = create_async_engine(url)
        try:
            async with engine.begin() as conn:
                if force:
                    console.print("[yellow]Dropping existing QSE tables...[/yellow]")
                    await conn.run_sync(Base.metadata.drop_all, tables=qse_tables)

                console.print("[blue]Creating QSE tables...[/blue]")
                await conn.run_sync(Base.metadata.create_all, tables=qse_tables)
                console.print("[green]QSE Database schema initialized successfully.[/green]")
        except Exception as e:
            console.print(f"[bold red]Initialization Failed:[/bold red] {e}")
            raise typer.Exit(code=1)
        finally:
            await engine.dispose()

    asyncio.run(_run())


if __name__ == "__main__":
    app()
