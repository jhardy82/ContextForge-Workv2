
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.db.connection_manager import ConnectionManager

# Mock settings
MOCK_PG_URL = "postgresql://user:pass@localhost:5432/db"
MOCK_SQLITE_PATH = "test.db"

# Mocking helper for async context managers
class MockAsyncContextManager:
    def __init__(self, target=None, side_effect=None):
        self.target = target
        self.side_effect = side_effect

    async def __aenter__(self):
        if self.side_effect:
            if isinstance(self.side_effect, Exception):
                raise self.side_effect
            return self.side_effect()
        return self.target

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_engines():
    with patch("taskman_api.db.connection_manager.create_async_engine") as mock_create:
        # Engines themselves don't need to be AsyncMock unless we call async methods on them
        primary_engine = MagicMock()
        fallback_engine = MagicMock()
        mock_create.side_effect = [primary_engine, fallback_engine]
        yield mock_create, primary_engine, fallback_engine

@pytest.fixture
def manager(mock_engines):
    # This triggers the mocked create_async_engine calls
    return ConnectionManager(MOCK_PG_URL, MOCK_SQLITE_PATH)

@pytest.mark.asyncio
async def test_init_creates_engines(mock_engines):
    mock_create, _, _ = mock_engines
    manager = ConnectionManager(MOCK_PG_URL, MOCK_SQLITE_PATH)

    assert mock_create.call_count == 2
    # Check Primary URL fix
    assert mock_create.call_args_list[0][0][0] == "postgresql+asyncpg://user:pass@localhost:5432/db"
    # Check Fallback URL
    assert mock_create.call_args_list[1][0][0] == f"sqlite+aiosqlite:///{MOCK_SQLITE_PATH}"

@pytest.mark.asyncio
async def test_get_session_primary_success(manager):
    # Setup mock session with proper context manager pattern
    mock_session = AsyncMock(spec=AsyncSession)
    manager.PrimarySession = MagicMock(return_value=MockAsyncContextManager(target=mock_session))

    # Run
    async for session in manager.get_session():
        assert session is mock_session

    # Verify
    manager.PrimarySession.assert_called_once()

@pytest.mark.asyncio
async def test_get_session_failover(manager):
    # Setup Primary to fail
    manager.PrimarySession = MagicMock(
        return_value=MockAsyncContextManager(side_effect=Exception("Connection Failed"))
    )

    # Setup Fallback to succeed
    mock_fallback_session = AsyncMock(spec=AsyncSession)
    manager.FallbackSession = MagicMock(
        return_value=MockAsyncContextManager(target=mock_fallback_session)
    )

    # Run
    async for session in manager.get_session():
        assert session is mock_fallback_session

    # Verify
    assert manager._using_fallback is True
    manager.PrimarySession.assert_called()
    manager.FallbackSession.assert_called()

@pytest.mark.asyncio
async def test_health_check_reporting(manager):
    # Mock Sessions for health check
    mock_primary = AsyncMock()
    mock_primary.execute = AsyncMock()

    mock_fallback = AsyncMock()
    mock_fallback.execute = AsyncMock()

    manager.PrimarySession = MagicMock(return_value=MockAsyncContextManager(target=mock_primary))
    manager.FallbackSession = MagicMock(return_value=MockAsyncContextManager(target=mock_fallback))

    # Run
    health = await manager.check_health()

    assert health["mode"] == "primary"
    assert health["primary"]["connected"] is True
    assert health["fallback"]["connected"] is True

@pytest.mark.asyncio
async def test_health_check_primary_down(manager):
    # Mock Primary Failure
    manager.PrimarySession = MagicMock(
        return_value=MockAsyncContextManager(side_effect=Exception("Down"))
    )

    # Mock Fallback Success
    mock_fallback = AsyncMock()
    manager.FallbackSession = MagicMock(return_value=MockAsyncContextManager(target=mock_fallback))

    # Run
    health = await manager.check_health()

    assert health["mode"] == "fallback"
    assert health["primary"]["connected"] is False
    assert health["fallback"]["connected"] is True
    assert manager._using_fallback is True

    assert health["mode"] == "fallback"
    assert health["primary"]["connected"] is False
    assert health["fallback"]["connected"] is True
    assert manager._using_fallback is True


@pytest.mark.asyncio
async def test_fix_async_url_logic():
    # Test static method directly
    url1 = ConnectionManager._fix_async_url("postgresql://user:pass@host/db")
    assert url1 == "postgresql+asyncpg://user:pass@host/db"

    url2 = ConnectionManager._fix_async_url("postgres://user:pass@host/db")
    assert url2 == "postgresql+asyncpg://user:pass@host/db"

    url3 = ConnectionManager._fix_async_url("sqlite:///taskman.db")
    assert url3 == "sqlite:///taskman.db"


@pytest.mark.asyncio
async def test_init_models(manager):
    # Mock engines to support begin() context manager
    manager.primary_engine = MagicMock()
    manager.primary_engine.begin.return_value = MockAsyncContextManager(target=AsyncMock())

    manager.fallback_engine = MagicMock()
    manager.fallback_engine.begin.return_value = MockAsyncContextManager(target=AsyncMock())

    # Mock Base class
    base_mock = MagicMock()

    # Act
    await manager.init_models(base_mock)

    # Assert
    manager.primary_engine.begin.assert_called_once()
    manager.fallback_engine.begin.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_all_fail(manager):
    # Setup Primary to fail
    manager.PrimarySession = MagicMock(
        return_value=MockAsyncContextManager(side_effect=Exception("Primary Down"))
    )

    # Setup Fallback to fail also
    manager.FallbackSession = MagicMock(
        return_value=MockAsyncContextManager(side_effect=Exception("Fallback Down"))
    )

    # Run & Assert
    with pytest.raises(Exception) as exc:
        async for _ in manager.get_session():
            pass

    assert "Fallback Down" in str(exc.value)


@pytest.mark.asyncio
async def test_health_check_all_down(manager):
    # Mock Primary Failure
    manager.PrimarySession = MagicMock(
        return_value=MockAsyncContextManager(side_effect=Exception("Primary Down"))
    )

    # Mock Fallback Failure
    manager.FallbackSession = MagicMock(
        return_value=MockAsyncContextManager(side_effect=Exception("Fallback Down"))
    )

    # Run
    health = await manager.check_health()

    assert (
        health["mode"] == "primary"
    )  # Defaults to primary if both fail or strictly depends on logic (logic says mode=fallback if fallback connected else primary)
    # Line 123: status["mode"] = "fallback" if self._using_fallback else "primary"
    # Line 116: if primary connected -> _using_fallback = False
    # Line 117: elif fallback connected -> _using_fallback = True
    # Line 120: else -> logger.critical
    # So if both fail, it stays whatever it was. Default is False (Primary).

    assert health["primary"]["connected"] is False
    assert health["primary"]["error"] == "Primary Down"
    assert health["fallback"]["connected"] is False
    assert health["fallback"]["error"] == "Fallback Down"


@pytest.mark.asyncio
async def test_init_models_failures(manager):
    manager.primary_engine = MagicMock()
    # Primary fails
    manager.primary_engine.begin.return_value = MockAsyncContextManager(
        side_effect=Exception("Init Fail")
    )

    manager.fallback_engine = MagicMock()
    # Fallback fails
    manager.fallback_engine.begin.return_value = MockAsyncContextManager(
        side_effect=Exception("Init Fail Fallback")
    )

    # Act (should log errors but not crash ideally, or re-raise? Code says log warning/error)
    # 175: logger.warning("primary_db_init_failed"...)
    # 183: logger.error("fallback_db_init_failed"...)

    await manager.init_models(MagicMock())
    # If it doesn't raise, test passes (verifying it swallows errors as per implementation)
