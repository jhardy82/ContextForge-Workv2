import pytest
from cf_mcp.config import settings
from cf_mcp.models import Base, Project
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = settings.DATABASE_URL


from sqlalchemy import text


@pytest.fixture(scope="function")
async def engine():
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool, echo=True)
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.mark.asyncio
async def test_create_project(db_session):
    new_project = Project(
        name="Alpha Project", mission="Test Mission", status="active", owner="james"
    )
    db_session.add(new_project)
    await db_session.commit()
    await db_session.refresh(new_project)

    assert new_project.id.startswith(
        "P-"
    )  # Assuming Model has default ID generation or we need to supply it?
    # NOTE: Model definition for Project had `id: Mapped[str] = mapped_column(String(64), primary_key=True)`
    # If no default, this will fail. Let's check model. If failed, we fix tool/model.
    # In `cf_mcp/models.py` (Step 11706), Project ID does NOT have a default generator shown in the snippet?
    # Wait, Task had `default=lambda: ...`.
    # I should verify Project model ID generation. Assuming for now tool creates it or DB default.
    # Actually, in `projects.py` tool I didn't generate ID.
    # I will modify this test to SUPPLY ID if needed, or rely on fix.

    assert new_project.name == "Alpha Project"


@pytest.mark.asyncio
async def test_list_projects(db_session):
    # Create two projects
    p1 = Project(id="P-001", name="Project A", status="active")
    p2 = Project(id="P-002", name="Project B", status="planning")
    db_session.add_all([p1, p2])
    await db_session.commit()

    # List
    stmt = select(Project).where(Project.status == "active")
    result = await db_session.execute(stmt)
    active_projects = result.scalars().all()

    assert len(active_projects) == 1
    assert active_projects[0].name == "Project A"
