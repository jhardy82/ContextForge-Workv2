from unittest.mock import AsyncMock

import pytest

from taskman_api.routers.agent import ChatRequest, chat_interaction


@pytest.mark.asyncio
async def test_agent_chat_navigation():
    repo = AsyncMock()
    mock_node = MagicMock()
    mock_node.id = "AUTH-001"
    mock_node.title = "Authentication"
    mock_node.kind = "component"
    repo.get_by_title_or_id.return_value = mock_node

    request = ChatRequest(message="Show me Authentication")
    response = await chat_interaction(request, repo)

    assert response.action == "navigate_context"
    assert response.data["id"] == "AUTH-001"

@pytest.mark.asyncio
async def test_agent_chat_unknown():
    repo = AsyncMock()
    repo.get_by_title_or_id.return_value = None

    request = ChatRequest(message="Hello world")
    response = await chat_interaction(request, repo)

    assert response.action is None
    assert "received your message" in response.message
