import asyncio
import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add src to python path to allow imports
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from taskman_api.db.session import manager
from taskman_api.models import Project, Sprint, Task
from taskman_api.schemas.project import ProjectStatus
from taskman_api.schemas.sprint import SprintStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")
console = Console()

TRACKERS_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "trackers"


class MigrationStats:
    def __init__(self):
        self.projects_found = 0
        self.projects_imported = 0
        self.sprints_found = 0
        self.sprints_imported = 0
        self.tasks_found = 0
        self.tasks_imported = 0
        self.errors = []

    def log_error(self, file_path: str, error: str):
        self.errors.append({"file": str(file_path), "error": str(error)})


stats = MigrationStats()


def parse_date(date_val: Any) -> str | None:
    if not date_val:
        return None
    if isinstance(date_val, (date, datetime)):
        return date_val.isoformat()
    if isinstance(date_val, str):
        try:
            return date.fromisoformat(date_val.split("T")[0]).isoformat()
        except ValueError:
            return None
    return None


def load_file(file_path: Path) -> dict[str, Any] | list[Any] | None:
    try:
        with open(file_path, encoding="utf-8") as f:
            if file_path.suffix == ".json":
                return json.load(f)
            elif file_path.suffix in (".yaml", ".yml"):
                return yaml.safe_load(f)
    except Exception:
        return None
    return {}


def extract_id_from_filename(file_path: Path, prefix: str) -> str | None:
    """Extract ID from filename if missing in data.
    e.g. project.P-123.yaml -> P-123
    """
    stem = file_path.stem  # e.g. project.P-123 or task.T-123
    parts = stem.split(".")
    if len(parts) > 1:
        # Check if any part looks like an ID
        for part in parts:
            if part.startswith(prefix) or (prefix == "S-" and part.startswith("S-")):
                return part
        # Return last part as fallback
        return parts[-1]
    return stem


def to_json(val: Any) -> str | None:
    """Serialize value to JSON string for Text columns."""
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return json.dumps(val)
    return str(val)


async def import_projects(session: AsyncSession, dry_run: bool):
    projects_dir = TRACKERS_DIR / "projects"
    # ... (code preserved)
    if not projects_dir.exists():
        console.print(f"[yellow]Projects directory not found: {projects_dir}[/yellow]")
        return

    try:
        existing_ids = (await session.execute(select(Project.id))).scalars().all()
        existing_set = set(existing_ids)
    except Exception as e:
        console.print(f"[red]Error fetching existing projects: {e}[/red]")
        existing_set = set()

    for file_path in projects_dir.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix not in (".json", ".yaml", ".yml"):
            continue

        stats.projects_found += 1
        try:
            data = load_file(file_path)
            if not isinstance(data, dict):
                data = {}  # Handle None or bad types by treating as empty dict and using fallback ID

            project_id = data.get("id")
            if not project_id:
                project_id = extract_id_from_filename(file_path, "P-")

            if not project_id:
                stats.log_error(file_path, "Could not determine Project ID")
                continue

            if project_id in existing_set:
                if not dry_run:
                    console.print(f"[dim]Skipping existing project: {project_id}[/dim]")
                continue
            existing_set.add(project_id)

            # Map fields for loose schema compatibility
            status_val = data.get("status", "new").upper()
            if status_val == "ACTIVE":
                status_val = "IN_PROGRESS"
            if status_val not in ProjectStatus.__members__:
                status_val = "NEW"

            create_data = {
                "id": project_id,
                "name": data.get("name", f"Unnamed Project {project_id}"),
                "mission": data.get("mission"),
                "status": status_val,
                "start_date": str(parse_date(data.get("start_date")))
                if parse_date(data.get("start_date"))
                else None,
                "target_end_date": str(parse_date(data.get("target_end_date")))
                if parse_date(data.get("target_end_date"))
                else None,
                "owner": data.get("owner"),
                "sponsors": to_json(data.get("sponsors", [])),
                "stakeholders": to_json(data.get("stakeholders", [])),
                "repositories": to_json(data.get("repositories", [])),
                "comms_channels": to_json(data.get("comms_channels", [])),
                "okrs": to_json(data.get("okrs", [])),
                "kpis": to_json(data.get("kpis", [])),
                "roadmap": to_json(data.get("roadmap", [])),
                "risks": to_json(data.get("risks", [])),
                "assumptions": to_json(data.get("assumptions", [])),
                "constraints": to_json(data.get("constraints", [])),
                "dependencies_external": to_json(data.get("dependencies_external", [])),
                "sprints": to_json(data.get("sprints", [])),
                "related_projects": to_json(data.get("related_projects", [])),
                "shared_components": to_json(data.get("shared_components", [])),
                "security_posture": to_json(data.get("security_posture")),
                "compliance_requirements": to_json(data.get("compliance_requirements", [])),
                "governance": to_json(data.get("governance", {})),
                "success_metrics": to_json(data.get("success_metrics", [])),
                "mpv_policy": to_json(data.get("mpv_policy", {})),
                "tnve_mandate": str(data.get("tnve_mandate")) if data.get("tnve_mandate") else None,
                "evidence_root": data.get("evidence_root"),
                # Removed observability as it differs from model
            }

            project = Project(**create_data)
            session.add(project)

            if not dry_run:
                stats.projects_imported += 1
                console.print(f"[green]Importing Project: {project_id}[/green]")
            else:
                console.print(f"[blue][DRY RUN] Staged Project: {project_id}[/blue]")

        except Exception as e:
            stats.log_error(file_path, str(e))
            console.print(f"[red]Error importing {file_path.name}: {e}[/red]")


async def import_sprints(session: AsyncSession, dry_run: bool):
    sprints_dir = TRACKERS_DIR / "sprints"
    if not sprints_dir.exists():
        return

    try:
        existing_ids = set((await session.execute(select(Sprint.id))).scalars().all())
    except Exception:
        existing_ids = set()

    for file_path in sprints_dir.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix not in (".json", ".yaml", ".yml"):
            continue
        stats.sprints_found += 1

        try:
            data = load_file(file_path)
            if not isinstance(data, dict):
                data = {}

            sprint_id = data.get("id")
            if not sprint_id:
                sprint_id = extract_id_from_filename(file_path, "S-")

            if not sprint_id or (sprint_id in existing_ids):
                continue
            existing_ids.add(sprint_id)

            status_val = data.get("status", "planned").upper()
            if status_val not in SprintStatus.__members__:
                status_val = "PLANNED"

            create_data = {
                "id": sprint_id,
                "name": data.get("name", sprint_id),
                "goal": data.get("goal"),
                "status": status_val,
                "start_date": parse_date(data.get("start_date")),
                "end_date": parse_date(data.get("end_date")),
                "owner": data.get("owner"),
                "project_id": data.get("primary_project"),
            }

            sprint = Sprint(**create_data)
            session.add(sprint)

            if not dry_run:
                stats.sprints_imported += 1
                console.print(f"[green]Importing Sprint: {sprint_id}[/green]")
            else:
                console.print(f"[blue][DRY RUN] Staged Sprint: {sprint_id}[/blue]")

        except Exception as e:
            stats.log_error(file_path, str(e))


async def import_tasks(session: AsyncSession, dry_run: bool):
    tasks_dir = TRACKERS_DIR / "tasks"
    if not tasks_dir.exists():
        return

    try:
        existing_ids = set((await session.execute(select(Task.id))).scalars().all())
    except Exception:
        existing_ids = set()

    for file_path in tasks_dir.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix not in (".json", ".yaml", ".yml"):
            continue
        stats.tasks_found += 1

        try:
            raw_data = load_file(file_path)

            # Unwrap list if necessary (some yaml files start with - task:)
            if isinstance(raw_data, list) and len(raw_data) > 0:
                raw_data = raw_data[0]

            if not isinstance(raw_data, dict):
                # Try to extract ID just to log better error or skip
                continue

            data = raw_data.get("task", raw_data)
            if not isinstance(data, dict):
                continue

            task_id = data.get("id")
            if not task_id:
                task_id = extract_id_from_filename(file_path, "T-")

            if not task_id or (task_id in existing_ids):
                continue
            existing_ids.add(task_id)

            status_val = data.get("status", "todo").replace(" ", "_").lower()
            status_map = {
                "new": "todo",
                "active": "in_progress",
                "closed": "done",
                "complete": "done",
            }
            status_val = status_map.get(status_val, status_val)

            prio = data.get("priority", "medium").lower()
            if prio == "p0":
                prio = "critical"
            elif prio == "p1":
                prio = "high"
            elif prio == "p2":
                prio = "medium"
            elif prio == "p3":
                prio = "low"

            t_type = "feature"
            if task_id.startswith("T-"):
                t_type = "task"

            prim_proj = data.get("primary_project", "")
            prim_sprint = data.get("primary_sprint", "")

            create_data = {
                "id": task_id,
                "title": data.get("title", f"Untitled Task {task_id}"),
                "description": data.get("description", ""),
                "status": status_val,
                "priority": prio,
                "work_type": t_type,
                "primary_project": prim_proj,
                "primary_sprint": prim_sprint,
                "project_id": prim_proj if prim_proj else None,
                "sprint_id": prim_sprint if prim_sprint else None,
                "owner": data.get("owner", "unassigned"),
                "created_at": None,
                "updated_at": None,
            }

            task = Task(**create_data)
            session.add(task)

            if not dry_run:
                stats.tasks_imported += 1
            else:
                pass

        except Exception as e:
            stats.log_error(file_path, str(e))


async def main(dry_run: bool = False, use_sqlite: bool = False):
    console.print(
        f"[bold]Starting Legacy Data Migration (Dry Run: {dry_run}, Use SQLite: {use_sqlite})[/bold]"
    )
    console.print(f"Trackers Directory: {TRACKERS_DIR}")

    if not TRACKERS_DIR.exists():
        console.print("[red]Trackers directory not found![/red]")
        return

    # Select session factory
    if use_sqlite:
        console.print("[yellow]Using SQLite (Fallback) Database[/yellow]")
        session_factory = manager.FallbackSession
    else:
        session_factory = manager.PrimarySession

    # Init models for fallback if needed
    if use_sqlite:
        from taskman_api.db.base import Base

        # Force strict schema reset for migration
        async with manager.fallback_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        console.print("[yellow]SQLite Schema Reset Complete[/yellow]")
        # await manager.init_models(Base) # Skip default init as we did it manually

    try:
        async with session_factory() as session:
            async with session.begin():
                await import_projects(session, dry_run)
                await import_sprints(session, dry_run)
                await import_tasks(session, dry_run)

                if dry_run:
                    await session.rollback()
                    console.print("[yellow]Dry run - Rolling back all changes[/yellow]")
                else:
                    pass
    except Exception as e:
        console.print(f"[red]Critical Session Error: {e}[/red]")
        if "ConnectionRefusedError" in str(e) or "The remote computer refused" in str(e):
            console.print(
                "[red]Could not connect to database. Ensure Docker is running (for Postgres) or use --use-sqlite[/red]"
            )

    # Report
    table = Table(title="Migration Summary")
    table.add_column("Type", style="cyan")
    table.add_column("Found", style="magenta")
    table.add_column("Imported", style="green")

    table.add_row("Projects", str(stats.projects_found), str(stats.projects_imported))
    table.add_row("Sprints", str(stats.sprints_found), str(stats.sprints_imported))
    table.add_row("Tasks", str(stats.tasks_found), str(stats.tasks_imported))

    console.print(table)

    if stats.errors:
        console.print(f"\n[red]Encoutered {len(stats.errors)} errors. See log for details.[/red]")
        with open("migration_errors.log", "w", encoding="utf-8") as f:
            for err in stats.errors:
                f.write(f"{err['file']}: {err['error']}\n")
        console.print("[yellow]Errors logged to migration_errors.log[/yellow]")


if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    use_sqlite = "--use-sqlite" in sys.argv
    asyncio.run(main(dry_run=is_dry_run, use_sqlite=use_sqlite))
