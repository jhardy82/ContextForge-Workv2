from unittest.mock import AsyncMock

import pytest

from taskman_api.routers.context import get_context
from taskman_api.schemas.context import ContextResponse


@pytest.mark.asyncio
async def test_get_context_found():
    repo = AsyncMock()
    repo.get_by_title_or_id.return_value = ContextResponse(
        id="C-001", title="Test Context", kind="feature", attributes={}
    )

    result = await get_context("C-001", repo, resolve=False)
    assert result.id == "C-001"
    assert result.title == "Test Context"

@pytest.mark.asyncio
async def test_get_context_not_found():
    repo = AsyncMock()
    repo.get_by_title_or_id.return_value = None

    with pytest.raises(Exception) as exc: # HTTPException
        await get_context("Invalid", repo, resolve=False)
    assert "not found" in str(exc.value)
