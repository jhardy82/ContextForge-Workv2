import pytest
import pytest_asyncio
from cf_mcp.config import settings
from cf_mcp.models import Base, Sprint
from cf_mcp.schemas import SprintCadence, SprintCreate, SprintStatus
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = settings.DATABASE_URL
# Use NullPool to avoid asyncpg loop attachment issues during tests
from sqlalchemy.pool import NullPool


@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool, echo=True)
    async with engine.begin() as conn:
        # Drop with CASCADE to handle foreign key dependencies (e.g. from existing backend-api tables)
        await conn.execute(text("DROP TABLE IF EXISTS sprints CASCADE"))
        # Also drop projects because sprints might reference it? Sprint model has project_id but no FK constraint defined in this model.
        # But let's be safe and consistent with other tests.
        await conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))

        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def db_session(engine):
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_create_sprint(db_session):
    new_sprint = Sprint(
        id="S-001",
        name="Sprint 1",
        status="planning",
        cadence="biweekly"
    )
    db_session.add(new_sprint)
    await db_session.commit()

    # Verify
    result = await db_session.get(Sprint, "S-001")
    assert result is not None
    assert result.name == "Sprint 1"
    assert result.status == "planning"

@pytest.mark.asyncio
async def test_list_sprints(db_session):
    s1 = Sprint(id="S-010", name="Sprint 10", status="active")
    s2 = Sprint(id="S-011", name="Sprint 11", status="planning")
    db_session.add_all([s1, s2])
    await db_session.commit()

    from sqlalchemy import select
    result = await db_session.execute(select(Sprint))
    sprints = result.scalars().all()
    assert len(sprints) == 2
