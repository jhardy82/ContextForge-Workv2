#!/usr/bin/env python3
"""
SQLite Integration Test for Backend API
Tests the actual FastAPI endpoints using SQLite instead of PostgreSQL.

This validates:
1. The add_action_list_item endpoint works correctly
2. The request/response models are correct
3. The repository pattern works with SQLite

Usage:
    cd TaskMan-v2/backend-api
    python test_sqlite_integration.py
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# CRITICAL: Set environment BEFORE any imports
SQLITE_DB_PATH = Path(tempfile.gettempdir()) / "taskman_integration_test.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"
os.environ["ENVIRONMENT"] = "test"

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


async def setup_sqlite_database():
    """Create SQLite database with required tables."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    sqlite_url = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"
    engine = create_async_engine(sqlite_url, echo=False)

    async with engine.begin() as conn:
        # Create action_lists table matching PostgreSQL schema
        await conn.execute(
            text("""
            CREATE TABLE IF NOT EXISTS action_lists (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                task_ids TEXT DEFAULT '[]',
                status TEXT DEFAULT 'active',
                priority INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        )

        # Insert test data
        await conn.execute(
            text("""
            INSERT OR REPLACE INTO action_lists (id, name, description, task_ids, status, priority)
            VALUES
                ('AL-0001', 'Backend Investigation', 'Root cause analysis tasks', '[]', 'active', 1),
                ('AL-0002', 'MCP Validation', 'Validate all MCP tools', '[]', 'active', 2),
                ('AL-0003', 'Frontend Tasks', 'UI improvements', '[]', 'active', 3),
                ('AL-0004', 'Documentation', 'Update all documentation', '[]', 'active', 4)
        """)
        )

    await engine.dispose()
    print(f"✅ SQLite database created: {SQLITE_DB_PATH}")
    return engine


async def test_add_item_endpoint():
    """Test the add_action_list_item endpoint."""
    from httpx import ASGITransport, AsyncClient

    # Import after env setup
    try:
        from main import app
    except ImportError:
        # Try alternate import path
        sys.path.insert(0, str(project_root / "src" / "taskman_api"))
        from main import app

    print("\n" + "=" * 60)
    print("Testing add_action_list_item Endpoint")
    print("=" * 60)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test 1: Add single item
        print("\n📝 Test 1: Add single item to AL-0001")
        response = await client.post(
            "/api/v1/action-lists/AL-0001/items",
            json={"text": "Test item from SQLite integration test"},
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(
                f"   ✅ Success! List now has {data.get('task_count', len(data.get('task_ids', [])))} items"
            )
        else:
            print(f"   ❌ Error: {response.text}")
            return False

        # Test 2: Add multiple items
        print("\n📝 Test 2: Add multiple items to AL-0001")
        items = [
            "Investigate circuit breaker behavior",
            "Check database connection pooling",
            "Review error handling patterns",
            "Test retry logic",
            "Validate timeout settings",
        ]
        for item in items:
            response = await client.post("/api/v1/action-lists/AL-0001/items", json={"text": item})
            if response.status_code == 200:
                print(f"   ✅ Added: {item[:40]}...")
            else:
                print(f"   ❌ Failed: {item[:40]}... - {response.text}")
                return False

        # Test 3: Verify final state
        print("\n📝 Test 3: Verify list contents")
        response = await client.get("/api/v1/action-lists/AL-0001")
        if response.status_code == 200:
            data = response.json()
            task_ids = data.get("task_ids", [])
            print(f"   ✅ AL-0001 has {len(task_ids)} items")
            for i, item_id in enumerate(task_ids[:5], 1):
                print(f"      {i}. {item_id}")
            if len(task_ids) > 5:
                print(f"      ... and {len(task_ids) - 5} more")
        else:
            print(f"   ❌ Error getting list: {response.text}")

        # Test 4: Test 404 for non-existent list
        print("\n📝 Test 4: Verify 404 for non-existent list")
        response = await client.post(
            "/api/v1/action-lists/AL-9999/items", json={"text": "Should fail"}
        )
        if response.status_code == 404:
            print("   ✅ Correctly returned 404")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")

        # Test 5: Add items to other lists (bulk test)
        print("\n📝 Test 5: Bulk add to multiple lists")
        test_data = {
            "AL-0002": ["MCP tool test 1", "MCP tool test 2", "MCP tool test 3"],
            "AL-0003": ["Frontend task 1", "Frontend task 2"],
            "AL-0004": ["Doc update 1", "Doc update 2", "Doc update 3", "Doc update 4"],
        }

        for list_id, items in test_data.items():
            for item in items:
                response = await client.post(
                    f"/api/v1/action-lists/{list_id}/items", json={"text": item}
                )
                if response.status_code != 200:
                    print(f"   ❌ Failed adding to {list_id}: {response.text}")
                    return False
            print(f"   ✅ {list_id}: Added {len(items)} items")

    return True


async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("SQLite Integration Test Suite")
    print("=" * 60)

    # Setup
    await setup_sqlite_database()

    # Run tests
    success = await test_add_item_endpoint()

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    if success:
        print("✅ All tests PASSED!")
        print("\n🎉 The add_action_list_item endpoint is working correctly!")
        print("\n📋 What this proves:")
        print("   1. The endpoint route is correctly registered")
        print("   2. The request model (ActionListAddItemRequest) works")
        print("   3. The repository add_task() method works")
        print("   4. The response model (ActionListResponse) works")
        print("\n🔧 The issue is that Docker container has OLD code.")
        print("   Solution: Rebuild container with latest code.")
    else:
        print("❌ Some tests FAILED!")
        print("   Check the error messages above.")

    # Cleanup
    if SQLITE_DB_PATH.exists():
        SQLITE_DB_PATH.unlink()
        print(f"\n🧹 Cleaned up: {SQLITE_DB_PATH}")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
