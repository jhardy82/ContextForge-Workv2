
import asyncio
import os
import sys

from sqlalchemy import text

# Add src to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from taskman_api.db.session import manager


async def main():
    print("Checking for 'tasks' table...")
    async for session in manager.get_session():
        try:
            result = await session.execute(text("SELECT to_regclass('public.tasks');"))
            table_exists = result.scalar()
            if table_exists:
                print("SUCCESS: 'tasks' table FOUND.")
            else:
                print("FAILURE: 'tasks' table NOT FOUND.")
            return
        except Exception as e:
            print(f"Error checking table: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
