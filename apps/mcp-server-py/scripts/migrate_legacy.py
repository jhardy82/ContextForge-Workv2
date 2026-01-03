import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cf_mcp.config import settings
from cf_mcp.models import Base, Context, Project, Sprint, Task
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Path to the dump file
DUMP_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "exports", "contextforge_dump.json")


async def migrate():
    print(f"🚀 Starting Migration from {DUMP_FILE}")

    if not os.path.exists(DUMP_FILE):
        print(f"❌ Dump file not found: {DUMP_FILE}")
        return

    with open(DUMP_FILE, encoding="utf-8") as f:
        data = json.load(f)

    projects_data = data.get("projects", [])
    sprints_data = data.get("sprints", [])
    tasks_data = data.get("tasks", [])

    print(
        f"📊 Found: {len(projects_data)} Projects, {len(sprints_data)} Sprints, {len(tasks_data)} Tasks"
    )

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            # 1. Projects
            print("📦 Migrating Projects...")
            for p_data in projects_data:
                # Handle dates
                created_at = parse_date(p_data.get("created_at"))
                start_date = parse_date(p_data.get("start_date"))
                target_date = parse_date(p_data.get("target_end_date"))
                completed_at = parse_date(p_data.get("actual_end_date"))

                project = Project(
                    id=p_data["id"],
                    name=p_data["name"],
                    mission=p_data.get("description"),  # Map description to mission
                    status=p_data.get("status", "active"),
                    owner=p_data.get("owner"),
                    created_at=created_at or datetime.now(),
                    start_date=start_date,
                    target_date=target_date,
                    completed_at=completed_at,
                    # JSON fields
                    tags=p_data.get("tags", []),
                    observability=p_data.get("observability", {}),
                    risks=json_safe(p_data.get("risks", [])),
                )
                await session.merge(project)  # Use merge to handle existing IDs

            await session.commit()
            print("✅ Projects Migrated")

            # 2. Sprints
            print("🏃 Migrating Sprints...")
            for s_data in sprints_data:
                sprint = Sprint(
                    id=s_data["id"],
                    title=s_data.get("title"),
                    goal=s_data.get("goal"),
                    status=s_data.get("status"),
                    project_id=s_data.get("project_id"),
                    start_date=s_data.get("start_date"),
                    end_date=s_data.get("end_date"),
                    created_at=s_data.get("created_at"),
                    # JSON fields
                    observability=json_safe(s_data.get("observability", {})),
                    risks=json_safe(s_data.get("risks", [])),
                )
                await session.merge(sprint)

            await session.commit()
            print("✅ Sprints Migrated")

            # 3. Tasks
            print("📝 Migrating Tasks...")
            for t_data in tasks_data:
                # Parse Dates
                created_at = parse_date(t_data.get("created_at"))

                task = Task(
                    id=t_data["id"],
                    title=t_data["title"],
                    description=t_data.get("description"),
                    status=t_data.get("status", "new"),
                    priority=str(
                        t_data.get("priority", "0")
                    ),  # Ensure string if model expects string
                    project_id=t_data.get("project_id"),  # Might be null in dump
                    sprint_id=t_data.get("sprint_id"),
                    # Core references
                    primary_project=t_data.get("primary_project"),
                    primary_sprint=t_data.get("primary_sprint"),
                    created_at=created_at or datetime.now(),
                    # JSON fields
                    tags=json_safe(t_data.get("tags", [])),
                    observability=json_safe(t_data.get("observability", {})),
                    acceptance_criteria=json_safe(t_data.get("acceptance_criteria", [])),
                )
                await session.merge(task)

            await session.commit()
            print("✅ Tasks Migrated")

        except Exception as e:
            print(f"❌ Migration Failed: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Tweak format as needed based on dump "2025-12-27 22:05:31.085391" or ISO
        if "T" in date_str:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        try:
            # Try without microseconds
            return datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        except:
            return None


def json_safe(val):
    """Ensure value is a valid Python object for JSON serialization key/values, or parse from string if it's a JSON string"""
    if isinstance(val, str):
        try:
            return json.loads(val)
        except:
            return []  # or return val if it's just a string, but here likely a serialized list
    return val


if __name__ == "__main__":
    asyncio.run(migrate())
