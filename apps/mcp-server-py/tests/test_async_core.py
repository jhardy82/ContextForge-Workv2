import asyncio
from datetime import datetime

import pytest
from cf_mcp.config import settings
from cf_mcp.models import Base, Task
from cf_mcp.schemas import TaskResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Use the configured database URL (from .env)
DATABASE_URL = settings.DATABASE_URL

# event_loop fixture removed to allow pytest-asyncio to manage loop lifecycle


@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_create_and_get_task(db_session):
    # 1. Create Task
    new_task = Task(
        title="Integration Test Task",
        description="Testing async persistence",
        status="new",
        priority="high",
    )
    db_session.add(new_task)
    await db_session.commit()
    await db_session.refresh(new_task)

    assert new_task.id.startswith("T-")
    assert new_task.title == "Integration Test Task"

    # 2. Retrieve Task by ID
    stmt = select(Task).where(Task.id == new_task.id)
    result = await db_session.execute(stmt)
    fetched_task = result.scalar_one()

    assert fetched_task.id == new_task.id
    assert fetched_task.description == "Testing async persistence"


@pytest.mark.asyncio
async def test_update_task(db_session):
    # Create
    task = Task(title="To Be Updated")
    db_session.add(task)
    await db_session.commit()

    # Update
    task.status = "in_progress"
    task.actual_hours = 1.5
    await db_session.commit()
    await db_session.refresh(task)

    assert task.status == "in_progress"
    assert task.actual_hours == 1.5


@pytest.mark.asyncio
async def test_delete_task(db_session):
    # Create
    task = Task(title="To Be Deleted")
    db_session.add(task)
    await db_session.commit()
    task_id = task.id

    # Delete
    await db_session.delete(task)
    await db_session.commit()

    # Verify
    stmt = select(Task).where(Task.id == task_id)
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None
