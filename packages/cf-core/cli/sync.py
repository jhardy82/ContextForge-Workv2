import asyncio
import os

import typer
from rich.console import Console
from rich.table import Table

from cf_core.cli.qse import get_service

app = typer.Typer(name="sync", help="Inline sync engine.", no_args_is_help=True)
console = Console()


@app.command()
def run(
    ctx: typer.Context,
    paths: list[str] = typer.Option(None, "--path", "-p", help="Paths to synchronize"),
    api_url: str = typer.Option(None, "--api", help="API URL to push results to"),
    task_id: str = typer.Option(None, "--task", help="Associated Task ID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate only"),
):
    """Run inline sync."""
    console.print(f"[bold blue]Running Inline Sync...[/bold blue] (Dry Run: {dry_run})")

    async def _run():
        try:
            # Check for API URL in env if not provided
            nonlocal api_url
            if not api_url:
                api_url = os.environ.get("CONTEXTFORGE_API_URL")

            service = await get_service(ctx)
            result = await service.sync_inline(paths=paths)

            if api_url and not dry_run:
                import requests

                console.print(f"Pushing results to {api_url}...")
                # Push Evidence
                for ev in result.get("evidence_collected", []):
                    # We can use the model's dict directly or map it
                    # Note: ev is a QSEEvidenceModel (SQLAlchemy)
                    payload = {
                        "artifact_type": ev.artifact_type,
                        "artifact_path": ev.artifact_path,
                        "artifact_hash": ev.artifact_hash,
                        "file_size_bytes": ev.file_size_bytes,
                        "task_id": ev.task_id,
                        "session_id": ev.session_id,
                        "metadata_": ev.metadata_,
                    }
                    endpoint = f"{api_url.rstrip('/')}/qse/evidence"
                    requests.post(endpoint, json=payload, timeout=10)

                # Ensure we commit local results too if not pushing everything?
                # Actually, sync_inline already wrote them to the session.
                await service.repo.commit()

                # Push Evaluations
                # Extract evidence IDs for the payload
                evidence_ids = [ev.id for ev in result.get("evidence_collected", [])]

                for g in result.get("gates_evaluated", []):
                    if g.get("status") != "skipped":
                        # Push to evaluate endpoint
                        eval_payload = {
                            "gate_name": g.get("gate_name"),
                            "actual_value": g.get("actual_value"),
                            "task_id": task_id,
                            "evidence_ids": evidence_ids,
                        }
                        endpoint = f"{api_url.rstrip('/')}/qse/evaluate"
                        requests.post(endpoint, json=eval_payload, timeout=10)

            # Display Results
            table = Table(title="Sync Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Status", str(result.get("status")))
            table.add_row("Evidence Collected", str(len(result.get("evidence_collected", []))))
            table.add_row("Gates Evaluated", str(len(result.get("gates_evaluated", []))))
            if api_url:
                table.add_row("API Target", api_url)

            console.print(table)
            # ... (rest of table display)

            if result.get("gates_evaluated"):
                gate_table = Table(title="Gate Evaluations")
                gate_table.add_column("Gate", style="cyan")
                gate_table.add_column("Status", style="green")
                gate_table.add_column("Reason", style="yellow")

                for g in result.get("gates_evaluated"):
                    gate_table.add_row(
                        str(g.get("gate_name")), str(g.get("status")), str(g.get("reason", ""))
                    )

                console.print(gate_table)

        except Exception as e:
            console.print(f"[bold red]Sync Failed:[/bold red] {e}")
            import traceback

            console.print(traceback.format_exc())
            raise typer.Exit(code=1)
        finally:
            if "service" in locals() and hasattr(service.repo, "session"):
                session = service.repo.session
                await session.close()
                if hasattr(session, "bind") and session.bind:
                    # Dispose the engine to ensure clean exit
                    await session.bind.dispose()

    # Use asyncio.run to execute the async function
    # Note: If running inside an existing loop (unlikely for CLI entry), handling is needed.
    # Typer is synchronous, so this is the correct entry point for async logic.
    asyncio.run(_run())


if __name__ == "__main__":
    app()
