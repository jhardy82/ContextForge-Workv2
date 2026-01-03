"""
Standalone Mock Verification for ConnectionManager.
Simulates database behavior without requiring drivers or real DBs.
"""

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock

# Mock imports BEFORE db.connection_manager is imported
sys.modules["sqlalchemy.ext.asyncio"] = MagicMock()
sys.modules["sqlalchemy.ext.asyncio"].create_async_engine = MagicMock()
sys.modules["sqlalchemy.ext.asyncio"].AsyncSession = MagicMock()
sys.modules["sqlalchemy.ext.asyncio"].async_sessionmaker = MagicMock()

import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import the manager logic (assuming it doesn't do top-level imports that fail)
# actually, it imports structlog, sqlalchemy, etc.
# We need to make sure those exist or are mocked.
# Assuming basic libs exist.

from db.connection_manager import ConnectionManager


async def run_mock_verification():
    print("=" * 60)
    print("MOCK Verification of ConnectionManager Logic")
    print("=" * 60)

    # 1. Setup Mocks
    mock_create_engine = sys.modules["sqlalchemy.ext.asyncio"].create_async_engine
    mock_primary_engine = AsyncMock()
    mock_fallback_engine = AsyncMock()
    mock_create_engine.side_effect = [mock_primary_engine, mock_fallback_engine]

    # 2. Initialize Manager
    print("[1] Initializing Manager...")
    try:
        mgr = ConnectionManager("postgresql://user:pass@host/db", "fallback.db")
        print("    ✅ Manager initialized")
    except Exception as e:
        print(f"    ❌ Initialization failed: {e}")
        return

    # 3. Test Failover Logic
    print("\n[2] Testing Failover Logic (Primary Fails)...")

    # Configure Session Mocks
    mock_primary_session = MagicMock()
    mock_primary_session.__aenter__.side_effect = Exception("Primary Down")
    mgr.PrimarySession = MagicMock(return_value=mock_primary_session)

    mock_fallback_session_ctx = MagicMock()
    mock_fallback_session = AsyncMock()
    mock_fallback_session_ctx.__aenter__.return_value = mock_fallback_session
    mgr.FallbackSession = MagicMock(return_value=mock_fallback_session_ctx)

    try:
        async for session in mgr.get_session():
            print("    ✅ Session yielded successfully")
            if session == mock_fallback_session:
                print("    ✅ Correctly switched to Fallback Session")
            else:
                print("    ❌ yielded wrong session")
    except Exception as e:
        print(f"    ❌ Failover failed: {e}")

    # 4. Verify State
    if mgr._using_fallback:
        print("    ✅ Manager state updated to _using_fallback=True")
    else:
        print("    ❌ Manager state did NOT update")


if __name__ == "__main__":
    asyncio.run(run_mock_verification())
