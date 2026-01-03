import asyncio
import os
import sys

# Ensure we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from cf_mcp.db import get_db_context
from cf_mcp.models import Project, Sprint, Task
from sqlalchemy import func, select


async def verify():
    print("🔍 Verifying Migration...")

    async with get_db_context() as session:
        # Count Projects
        result = await session.execute(select(func.count(Project.id)))
        p_count = result.scalar()
        print(f"📦 Projects: {p_count}")

        # Count Sprints
        result = await session.execute(select(func.count(Sprint.id)))
        s_count = result.scalar()
        print(f"🏃 Sprints: {s_count}")

        # Count Tasks
        result = await session.execute(select(func.count(Task.id)))
        t_count = result.scalar()
        print(f"📝 Tasks: {t_count}")

        if p_count > 0:
            print("✅ Verification SUCCESS: Data found.")
        else:
            print("❌ Verification FAILED: Missing data.")


if __name__ == "__main__":
    asyncio.run(verify())
