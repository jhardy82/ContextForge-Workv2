"""Checklist API endpoints.

Provides REST endpoints for checklist management.
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_checklist_service
from taskman_api.schemas.checklist import (
    ChecklistCreateRequest,
    ChecklistItemAddRequest,
    ChecklistResponse,
    ChecklistUpdateRequest,
)
from taskman_api.services.checklist_service import ChecklistService

router = APIRouter()


# =========================================================================
# Search and Queries (MUST come before parametric routes)
# =========================================================================


@router.get("/checklists/search", response_model=list[ChecklistResponse])
async def search_checklists(
    status: str | None = None,
    is_template: bool | None = None,
    task_id: str | None = None,
    plan_id: str | None = None,
    conversation_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ChecklistService = Depends(get_checklist_service),
):
    """Search checklists with filters.

    Args:
        status: Filter by status
        is_template: Filter by template flag
        task_id: Filter by task
        plan_id: Filter by plan
        conversation_id: Filter by conversation
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Checklist service instance

    Returns:
        Filtered list of checklists
    """
    result = await service.search(
        status=status,
        is_template=is_template,
        task_id=task_id,
        plan_id=plan_id,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    match result:
        case Ok(checklists):
            return checklists
        case Err(error):
            raise error


@router.get("/checklists/templates", response_model=list[ChecklistResponse])
async def get_templates(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ChecklistService = Depends(get_checklist_service),
):
    """Get all checklist templates.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Checklist service instance

    Returns:
        List of templates
    """
    result = await service.get_templates(limit=limit, offset=offset)

    match result:
        case Ok(checklists):
            return checklists
        case Err(error):
            raise error


@router.get("/checklists/active", response_model=list[ChecklistResponse])
async def get_active_checklists(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ChecklistService = Depends(get_checklist_service),
):
    """Get all active checklists.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Checklist service instance

    Returns:
        List of active checklists
    """
    result = await service.get_active(limit=limit, offset=offset)

    match result:
        case Ok(checklists):
            return checklists
        case Err(error):
            raise error


@router.get("/checklists/blocked", response_model=list[ChecklistResponse])
async def get_checklists_with_blocked_items(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ChecklistService = Depends(get_checklist_service),
):
    """Get checklists with blocked items.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Checklist service instance

    Returns:
        List of checklists with blocked items
    """
    result = await service.get_with_blocked_items(limit=limit, offset=offset)

    match result:
        case Ok(checklists):
            return checklists
        case Err(error):
            raise error


@router.get("/checklists/stats")
async def get_checklist_stats(
    service: ChecklistService = Depends(get_checklist_service),
):
    """Get checklist statistics.

    Args:
        service: Checklist service instance

    Returns:
        Statistics dict
    """
    result = await service.get_stats()

    match result:
        case Ok(stats):
            return stats
        case Err(error):
            raise error


@router.get("/checklists/incomplete", response_model=list[ChecklistResponse])
async def get_incomplete_checklists(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ChecklistService = Depends(get_checklist_service),
):
    """Get incomplete checklists (active with pending items).

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Checklist service instance

    Returns:
        List of incomplete checklists
    """
    result = await service.get_incomplete(limit=limit, offset=offset)

    match result:
        case Ok(checklists):
            return checklists
        case Err(error):
            raise error


@router.post(
    "/checklists/from-template",
    status_code=status.HTTP_201_CREATED,
    response_model=ChecklistResponse,
)
async def create_from_template(
    template_id: str,
    title: str | None = None,
    task_id: str | None = None,
    plan_id: str | None = None,
    conversation_id: str | None = None,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Create a checklist from a template.

    Args:
        template_id: Source template ID
        title: Optional override title
        task_id: Optional task association
        plan_id: Optional plan association
        conversation_id: Optional conversation association
        service: Checklist service instance

    Returns:
        Created checklist

    Raises:
        404: Template not found
        422: Source is not a template
    """
    result = await service.create_from_template(
        template_id=template_id,
        title=title,
        task_id=task_id,
        plan_id=plan_id,
        conversation_id=conversation_id,
    )

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


# =========================================================================
# Checklist CRUD
# =========================================================================


@router.post(
    "/checklists",
    status_code=status.HTTP_201_CREATED,
    response_model=ChecklistResponse,
)
async def create_checklist(
    request: ChecklistCreateRequest,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Create a new checklist.

    Args:
        request: Checklist creation request
        service: Checklist service instance

    Returns:
        Created checklist

    Raises:
        409: Checklist with ID already exists
        422: Validation error
    """
    result = await service.create(request)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.get("/checklists/{checklist_id}", response_model=ChecklistResponse)
async def get_checklist(
    checklist_id: str,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Get checklist by ID.

    Args:
        checklist_id: Checklist identifier
        service: Checklist service instance

    Returns:
        Checklist details

    Raises:
        404: Checklist not found
    """
    result = await service.get(checklist_id)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.patch("/checklists/{checklist_id}", response_model=ChecklistResponse)
async def update_checklist(
    checklist_id: str,
    request: ChecklistUpdateRequest,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Update checklist with partial fields.

    Args:
        checklist_id: Checklist identifier
        request: Update request with optional fields
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist not found
        422: Validation error
    """
    result = await service.update(checklist_id, request)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.delete("/checklists/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: str,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Delete checklist by ID.

    Args:
        checklist_id: Checklist identifier
        service: Checklist service instance

    Returns:
        No content

    Raises:
        404: Checklist not found
    """
    result = await service.delete(checklist_id)

    match result:
        case Ok(_):
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        case Err(error):
            raise error


@router.get("/checklists", response_model=list[ChecklistResponse])
async def list_checklists(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ChecklistService = Depends(get_checklist_service),
):
    """List checklists with pagination.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Checklist service instance

    Returns:
        List of checklists
    """
    result = await service.list(limit=limit, offset=offset)

    match result:
        case Ok(checklists):
            return checklists
        case Err(error):
            raise error


# =========================================================================
# Checklist Lifecycle Operations
# =========================================================================


@router.post("/checklists/{checklist_id}/complete", response_model=ChecklistResponse)
async def complete_checklist(
    checklist_id: str,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Mark checklist as completed.

    Args:
        checklist_id: Checklist identifier
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist not found
    """
    result = await service.complete(checklist_id)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.post("/checklists/{checklist_id}/archive", response_model=ChecklistResponse)
async def archive_checklist(
    checklist_id: str,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Archive a checklist.

    Args:
        checklist_id: Checklist identifier
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist not found
    """
    result = await service.archive(checklist_id)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


# =========================================================================
# Item Operations
# =========================================================================


@router.post("/checklists/{checklist_id}/items/{item_id}/check", response_model=ChecklistResponse)
async def check_item(
    checklist_id: str,
    item_id: str,
    notes: str | None = None,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Mark an item as completed.

    Args:
        checklist_id: Checklist identifier
        item_id: Item identifier
        notes: Optional completion notes
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist or item not found
        422: Item is already completed
    """
    result = await service.check_item(checklist_id, item_id, notes)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.post("/checklists/{checklist_id}/items/{item_id}/uncheck", response_model=ChecklistResponse)
async def uncheck_item(
    checklist_id: str,
    item_id: str,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Mark a completed item as pending again.

    Args:
        checklist_id: Checklist identifier
        item_id: Item identifier
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist or item not found
        422: Item is not completed
    """
    result = await service.uncheck_item(checklist_id, item_id)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.post("/checklists/{checklist_id}/items/{item_id}/block", response_model=ChecklistResponse)
async def block_item(
    checklist_id: str,
    item_id: str,
    reason: str | None = None,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Mark an item as blocked.

    Args:
        checklist_id: Checklist identifier
        item_id: Item identifier
        reason: Optional block reason
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist or item not found
        422: Item is already blocked
    """
    result = await service.block_item(checklist_id, item_id, reason)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.post("/checklists/{checklist_id}/items/{item_id}/unblock", response_model=ChecklistResponse)
async def unblock_item(
    checklist_id: str,
    item_id: str,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Unblock a blocked item.

    Args:
        checklist_id: Checklist identifier
        item_id: Item identifier
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist or item not found
        422: Item is not blocked
    """
    result = await service.unblock_item(checklist_id, item_id)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.post("/checklists/{checklist_id}/items", response_model=ChecklistResponse)
async def add_item(
    checklist_id: str,
    item: ChecklistItemAddRequest,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Add an item to a checklist.

    Args:
        checklist_id: Checklist identifier
        item: Item to add (title, priority, etc.)
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist not found
    """
    result = await service.add_item(checklist_id, item, item.after_item_id)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error


@router.delete("/checklists/{checklist_id}/items/{item_id}", response_model=ChecklistResponse)
async def remove_item(
    checklist_id: str,
    item_id: str,
    service: ChecklistService = Depends(get_checklist_service),
):
    """Remove an item from a checklist.

    Args:
        checklist_id: Checklist identifier
        item_id: Item identifier
        service: Checklist service instance

    Returns:
        Updated checklist

    Raises:
        404: Checklist or item not found
    """
    result = await service.remove_item(checklist_id, item_id)

    match result:
        case Ok(checklist):
            return checklist
        case Err(error):
            raise error
