"""
Verify Database Connection Manager.
Tests dual-database logic by attempting to connect to configured Postgres (mock) and SQLite (real).
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import check_db_health, init_db, manager
from sqlalchemy import text


async def verify_dual_db():
    print("=" * 60)
    print("Dual-Database Connectivity Verification")
    print("=" * 60)

    print(f"Primary URL: {manager.primary_url}")
    print(f"Fallback URL: {manager.sqlite_url}")
    print()

    # 1. Init DBs
    print("1. Initializing Tables...")
    try:
        await init_db()
        print("   ✅ Initialization call completed")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")

    # 2. Check Health
    print("\n2. Checking Health...")
    health = await check_db_health()
    print(f"   Mode: {health['mode'].upper()}")
    print(f"   Primary: {health['primary']}")
    print(f"   Fallback: {health['fallback']}")

    if health['primary']['connected']:
        print("   ✅ Primary is UP")
    else:
        print("   ⚠️ Primary is DOWN (Expected if no Postgres running)")

    if health['fallback']['connected']:
        print("   ✅ Fallback is UP")
    else:
        print("   ❌ Fallback is DOWN")

    # 3. Get Session (Resilience Test)
    print("\n3. Testing Session Acquisition...")
    try:
        async for session in manager.get_session():
            result = await session.execute(text("SELECT 1"))
            print(f"   ✅ Got valid session! Result: {result.scalar()}")
            break
    except Exception as e:
        print(f"   ❌ Failed to get session: {e}")

if __name__ == "__main__":
    asyncio.run(verify_dual_db())
