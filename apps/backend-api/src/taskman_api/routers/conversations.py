"""Conversation API endpoints.

Provides REST endpoints for conversation session management.
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_conversation_service
from taskman_api.schemas.conversation import (
    ConversationSessionCreateRequest,
    ConversationSessionResponse,
    ConversationSessionUpdateRequest,
    ConversationTurnCreateRequest,
    ConversationTurnResponse,
)
from taskman_api.services.conversation_service import ConversationSessionService

router = APIRouter()


# =========================================================================
# Search and Queries (MUST come before parametric routes)
# =========================================================================


@router.get("/conversations/search", response_model=list[ConversationSessionResponse])
async def search_conversations(
    status: str | None = None,
    project_id: str | None = None,
    worktree: str | None = None,
    agent_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Search conversations with filters.

    Args:
        status: Filter by status
        project_id: Filter by project
        worktree: Filter by worktree
        agent_type: Filter by agent type
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Conversation service instance

    Returns:
        Filtered list of conversations
    """
    result = await service.search(
        status=status,
        project_id=project_id,
        worktree=worktree,
        agent_type=agent_type,
        limit=limit,
        offset=offset,
    )

    match result:
        case Ok(convs):
            return convs
        case Err(error):
            raise error


@router.get("/conversations/active", response_model=list[ConversationSessionResponse])
async def get_active_conversations(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Get all active conversations.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Conversation service instance

    Returns:
        List of active conversations
    """
    result = await service.get_active(limit=limit, offset=offset)

    match result:
        case Ok(convs):
            return convs
        case Err(error):
            raise error


@router.get("/conversations/stats")
async def get_conversation_stats(
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Get conversation statistics.

    Args:
        service: Conversation service instance

    Returns:
        Statistics dict
    """
    result = await service.get_stats()

    match result:
        case Ok(stats):
            return stats
        case Err(error):
            raise error


# =========================================================================
# Conversation Session CRUD
# =========================================================================


@router.post(
    "/conversations",
    status_code=status.HTTP_201_CREATED,
    response_model=ConversationSessionResponse,
)
async def create_conversation(
    request: ConversationSessionCreateRequest,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Create a new conversation session.

    Args:
        request: Conversation creation request
        service: Conversation service instance

    Returns:
        Created conversation

    Raises:
        409: Conversation with ID already exists
        422: Validation error
    """
    result = await service.create(request)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.get("/conversations/{conversation_id}", response_model=ConversationSessionResponse)
async def get_conversation(
    conversation_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Get conversation by ID.

    Args:
        conversation_id: Conversation identifier
        service: Conversation service instance

    Returns:
        Conversation details

    Raises:
        404: Conversation not found
    """
    result = await service.get(conversation_id)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.patch("/conversations/{conversation_id}", response_model=ConversationSessionResponse)
async def update_conversation(
    conversation_id: str,
    request: ConversationSessionUpdateRequest,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Update conversation with partial fields.

    Args:
        conversation_id: Conversation identifier
        request: Update request with optional fields
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
        422: Validation error
    """
    result = await service.update(conversation_id, request)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Delete conversation by ID.

    Args:
        conversation_id: Conversation identifier
        service: Conversation service instance

    Returns:
        No content

    Raises:
        404: Conversation not found
    """
    result = await service.delete(conversation_id)

    match result:
        case Ok(_):
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        case Err(error):
            raise error


@router.get("/conversations", response_model=list[ConversationSessionResponse])
async def list_conversations(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """List conversations with pagination.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Conversation service instance

    Returns:
        List of conversations
    """
    result = await service.list(limit=limit, offset=offset)

    match result:
        case Ok(convs):
            return convs
        case Err(error):
            raise error


# =========================================================================
# Conversation Lifecycle Operations
# =========================================================================


@router.post(
    "/conversations/{conversation_id}/complete",
    response_model=ConversationSessionResponse,
)
async def complete_conversation(
    conversation_id: str,
    summary: str | None = None,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Mark conversation as completed.

    Args:
        conversation_id: Conversation identifier
        summary: Optional final summary
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
    """
    result = await service.complete(conversation_id, summary)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.post(
    "/conversations/{conversation_id}/pause",
    response_model=ConversationSessionResponse,
)
async def pause_conversation(
    conversation_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Pause an active conversation.

    Args:
        conversation_id: Conversation identifier
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
    """
    result = await service.pause(conversation_id)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.post(
    "/conversations/{conversation_id}/resume",
    response_model=ConversationSessionResponse,
)
async def resume_conversation(
    conversation_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Resume a paused conversation.

    Args:
        conversation_id: Conversation identifier
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
        422: Invalid status for resume
    """
    result = await service.resume(conversation_id)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.post(
    "/conversations/{conversation_id}/archive",
    response_model=ConversationSessionResponse,
)
async def archive_conversation(
    conversation_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Archive a conversation.

    Args:
        conversation_id: Conversation identifier
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
    """
    result = await service.archive(conversation_id)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


# =========================================================================
# Conversation Turns
# =========================================================================


@router.post(
    "/conversations/{conversation_id}/turns",
    status_code=status.HTTP_201_CREATED,
    response_model=ConversationTurnResponse,
)
async def add_turn(
    conversation_id: str,
    request: ConversationTurnCreateRequest,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Add a turn to a conversation.

    Args:
        conversation_id: Conversation identifier
        request: Turn creation request
        service: Conversation service instance

    Returns:
        Created turn

    Raises:
        404: Conversation not found
    """
    result = await service.add_turn(conversation_id, request)

    match result:
        case Ok(turn):
            return turn
        case Err(error):
            raise error


@router.get(
    "/conversations/{conversation_id}/turns",
    response_model=list[ConversationTurnResponse],
)
async def get_turns(
    conversation_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Get turns for a conversation.

    Args:
        conversation_id: Conversation identifier
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Conversation service instance

    Returns:
        List of turns

    Raises:
        404: Conversation not found
    """
    result = await service.get_turns(conversation_id, limit, offset)

    match result:
        case Ok(turns):
            return turns
        case Err(error):
            raise error


# =========================================================================
# Linking Operations
# =========================================================================


@router.post(
    "/conversations/{conversation_id}/link-plan",
    response_model=ConversationSessionResponse,
)
async def link_plan(
    conversation_id: str,
    plan_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Link a plan to this conversation.

    Args:
        conversation_id: Conversation identifier
        plan_id: Plan ID to link
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
    """
    result = await service.link_plan(conversation_id, plan_id)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.post(
    "/conversations/{conversation_id}/link-checklist",
    response_model=ConversationSessionResponse,
)
async def link_checklist(
    conversation_id: str,
    checklist_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Link a checklist to this conversation.

    Args:
        conversation_id: Conversation identifier
        checklist_id: Checklist ID to link
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
    """
    result = await service.link_checklist(conversation_id, checklist_id)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error


@router.post(
    "/conversations/{conversation_id}/link-task",
    response_model=ConversationSessionResponse,
)
async def link_task(
    conversation_id: str,
    task_id: str,
    service: ConversationSessionService = Depends(get_conversation_service),
):
    """Link a task to this conversation.

    Args:
        conversation_id: Conversation identifier
        task_id: Task ID to link
        service: Conversation service instance

    Returns:
        Updated conversation

    Raises:
        404: Conversation not found
    """
    result = await service.link_task(conversation_id, task_id)

    match result:
        case Ok(conv):
            return conv
        case Err(error):
            raise error
