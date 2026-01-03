import pytest
import pytest_asyncio
from cf_mcp.config import settings
from cf_mcp.models import Base, Context
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = settings.DATABASE_URL
from sqlalchemy.pool import NullPool


# Use function scope for engine to ensure clean state per test run (now only 1 run)
@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool, echo=True)
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS contexts CASCADE"))
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_context_scenarios(db_session):
    """
    Run all context scenarios in a single async test to avoid
    pytest-asyncio/asyncpg loop teardown issues in WSL environment.
    """

    # Scenario 1: Create & Get
    print("\n--- Scenario 1: Create ---")
    new_context = Context(
        id="C-001",
        kind="domain",
        title="Software Engineering",
        confidence=0.9,
        dim_knowledge="High",
        dim_motivational="High",
    )
    db_session.add(new_context)
    await db_session.commit()

    result = await db_session.get(Context, "C-001")
    assert result is not None
    assert result.title == "Software Engineering"
    assert result.dim_knowledge == "High"

    # Scenario 2: Hierarchy (Parent/Child)
    print("\n--- Scenario 2: Hierarchy ---")
    parent = Context(id="C-ROOT", kind="root", title="Root Context")
    db_session.add(parent)
    await db_session.commit()

    child = Context(id="C-CHILD", kind="leaf", title="Child Context", parent_id="C-ROOT")
    db_session.add(child)
    await db_session.commit()

    # Need to verify persistence and relationship
    # Clear session to ensure we fetch from DB
    await db_session.commit()

    result_parent = await db_session.execute(select(Context).where(Context.id == "C-ROOT"))
    parent_loaded = result_parent.scalar_one()

    # Eager load children? Or just check child's parent_id?
    # Relationship loading requires explicit options in async usually,
    # but let's check basic FK integrity
    result_child = await db_session.execute(select(Context).where(Context.id == "C-CHILD"))
    child_loaded = result_child.scalar_one()
    assert child_loaded.parent_id == "C-ROOT"

    # Scenario 3: Search
    print("\n--- Scenario 3: Search ---")
    c1 = Context(title="Project Alpha", kind="project", summary="Important initiative")
    c2 = Context(title="Project Beta", kind="project", summary="Secondary initiative")
    db_session.add_all([c1, c2])
    await db_session.commit()

    result = await db_session.execute(select(Context).where(Context.title.ilike("%Alpha%")))
    items = result.scalars().all()
    assert len(items) == 1
    assert items[0].title == "Project Alpha"
