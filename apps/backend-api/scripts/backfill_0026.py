import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select, update

from taskman_api.db.session import async_session_factory
from taskman_api.models.project import Project
from taskman_api.models.sprint import Sprint


async def backfill_data():
    print("Starting backfill for Migration 0026...")

    async with async_session_factory() as session:
        print("Connected to database.")

        # 1. Backfill Sprints
        # Sprints need 'owner' and 'cadence'
        result = await session.execute(
            select(Sprint).where((Sprint.owner.is_(None)) | (Sprint.cadence.is_(None)))
        )
        sprints = result.scalars().all()

        if sprints:
            print(f"Found {len(sprints)} sprints to backfill.")
            stmt = (
                update(Sprint)
                .where((Sprint.owner.is_(None)) | (Sprint.cadence.is_(None)))
                .values(owner="admin", cadence="biweekly")
            )
            await session.execute(stmt)
            print("Sprints updated.")
        else:
            print("No sprints need backfilling.")

        # 2. Backfill Projects
        # Projects need 'labels', 'team_members', 'sprints'
        # We'll set them to empty JSON lists "[]" if they represent lists, or just empty strings/nulls?
        # Schema says List[str] -> likely stored as JSON text.
        # Let's check logic: models/projects.py says `labels: Mapped[str | None] = mapped_column(Text, nullable=True)`
        # Pydantic schemas/projects.py says `labels: list[str] = Field(default_factory=list)`
        # The validator `parse_json_list_str` handles JSON string parsing.
        # So we should set them to '[]'.

        result_proj = await session.execute(
            select(Project).where(
                (Project.labels.is_(None)) |
                (Project.team_members.is_(None)) |
                (Project.sprints.is_(None))
            )
        )
        projects = result_proj.scalars().all()

        if projects:
            print(f"Found {len(projects)} projects to backfill.")
            stmt_proj = (
                update(Project)
                .where(Project.labels.is_(None))
                .values(labels='[]')
            )
            await session.execute(stmt_proj)

            stmt_proj_tm = (
                update(Project)
                .where(Project.team_members.is_(None))
                .values(team_members='[]')
            )
            await session.execute(stmt_proj_tm)

            stmt_proj_sp = (
                update(Project)
                .where(Project.sprints.is_(None))
                .values(sprints='[]')
            )
            await session.execute(stmt_proj_sp)
            print("Projects updated.")
        else:
            print("No projects need backfilling.")

        await session.commit()
        print("Backfill complete.")

if __name__ == "__main__":
    try:
        asyncio.run(backfill_data())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
