#!/usr/bin/env python
"""Debug the task repository."""
import asyncio

from db import get_async_session
from repositories import TaskRepository


async def main():
    async for session in get_async_session():
        repo = TaskRepository(session)

        # Test get_all
        all_tasks = await repo.get_all()
        print(f"get_all() returned: {len(all_tasks)} tasks")
        for t in all_tasks:
            print(f"  - {t.id}: {t.title}")

        # Test search
        tasks, total = await repo.search()
        print(f"search() returned: {len(tasks)} tasks, total={total}")
        for t in tasks:
            print(f"  - {t.id}: {t.title}")

        # Test count
        count = await repo.count()
        print(f"count() returned: {count}")
        break


if __name__ == "__main__":
    asyncio.run(main())
