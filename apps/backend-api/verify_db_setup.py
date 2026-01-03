import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from sqlalchemy.ext.asyncio import create_async_engine

from taskman_api.db.base import Base

# Import models to register them with Base


async def main():
    print("Creating engine...", flush=True)
    try:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
        async with engine.begin() as conn:
            print("Creating tables...", flush=True)
            await conn.run_sync(Base.metadata.create_all)
        print("Success!", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
