import asyncio
import os
import sys

from sqlalchemy import text

# Add parent dir to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.base import Base
from db.session import manager


async def reset_database():
    print("--- NUCLEAR DATABASE RESET (FORCE) ---")
    try:
        # Import models to populate Base.metadata
        from models.task import Task

        # Verify Model Definition
        print(f"DEBUG: Python Model 'Task' columns: {[c.name for c in Task.__table__.columns]}")

        print(f"DEBUG: Connecting to: {manager.primary_engine.url}")

        async with manager.primary_engine.begin() as conn:
            print("Force Dropping tables via SQL...")
            await conn.execute(text("DROP TABLE IF EXISTS tasks CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS projects CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS sprints CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS action_lists CASCADE"))

            print("Creating all tables via Metadata...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Reset Complete.")

            # Inspect columns in DB
            from sqlalchemy import inspect

            def inspect_table(connection):
                inspector = inspect(connection)
                columns = [c["name"] for c in inspector.get_columns("tasks")]
                print(f"DEBUG: DB 'tasks' table columns: {columns}")

            await conn.run_sync(inspect_table)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback

        traceback.print_exc()
    print("--- END RESET ---")


if __name__ == "__main__":
    asyncio.run(reset_database())
