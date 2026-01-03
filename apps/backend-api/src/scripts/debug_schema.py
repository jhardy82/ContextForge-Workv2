import asyncio
import sys
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine

# Add src to python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
sys.path.append(str(src_dir))

from taskman_api.models import Project


async def main():
    db_path = "taskman.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(db_url)

    print(f"Inspecting DB: {db_url}")

    # Check what SQLAlchemy thinks the model is
    print("Model Columns:")
    for col in Project.__table__.columns:
        print(f" - {col.name}: {col.type}")

    # Check actual DB
    async with engine.connect() as conn:
        def get_columns(connection):
            inspector = inspect(connection)
            if inspector.has_table("projects"):
                return inspector.get_columns("projects")
            return []

        columns = await conn.run_sync(get_columns)
        print("\nActual Table Columns:")
        if not columns:
            print("Table 'projects' does not exist.")
        for col in columns:
            print(f" - {col['name']}: {col['type']}")

if __name__ == "__main__":
    asyncio.run(main())
