import asyncio
import os
import sys

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from cf_mcp.db import get_db
from sqlalchemy import text


async def verify_db():
    print("Verifying Database Connectivity...")
    try:
        async for session in get_db():
            result = await session.execute(text("SELECT 1"))
            print(f"Result: {result.scalar()}")
        print("SUCCESS: Connected to PostgreSQL!")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify_db())
