import asyncio

from db.session import get_async_session
from models.task import Task
from schemas.enums import TaskPriority, TaskStatus


async def seed_task():
    async for session in get_async_session():
        new_task = Task(
            id="T-SEED-001",
            title="Verify Greenfield Dashboard",
            summary="Verify data binding on the main dashboard",
            description="This task was created to verify the Greenfield Dashboard data binding.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.P1,
            owner="James",
            assignees=["James"],
            primary_project="PRJ-GREEN-001",
            primary_sprint="SPR-MVP-001",
        )
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)
        print(f"Created Task: {new_task.id} - {new_task.title}")

if __name__ == "__main__":
    asyncio.run(seed_task())
