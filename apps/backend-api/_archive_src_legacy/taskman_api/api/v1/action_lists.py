"""ActionList API endpoints.

Provides 5 REST endpoints for action list management.
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from taskman_api.api.deps import get_action_list_service
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.action_list import (
    ActionListCreateRequest,
    ActionListResponse,
    ActionListUpdateRequest,
)
from taskman_api.services.action_list_service import ActionListService

router = APIRouter()


@router.post(
    "/action-lists",
    status_code=status.HTTP_201_CREATED,
    response_model=ActionListResponse,
)
async def create_action_list(
    request: ActionListCreateRequest,
    service: ActionListService = Depends(get_action_list_service),
) -> ActionListResponse:
    """Create a new action list.

    Args:
        request: ActionList creation request with all required fields
        service: ActionList service instance

    Returns:
        Created action list

    Raises:
        409: ActionList with ID already exists
        422: Validation error
    """
    result = await service.create(request)

    match result:
        case Ok(action_list):
            return action_list
        case Err(error):
            raise error


@router.get("/action-lists/{list_id}", response_model=ActionListResponse)
async def get_action_list(
    list_id: str,
    service: ActionListService = Depends(get_action_list_service),
) -> ActionListResponse:
    """Get action list by ID.

    Args:
        list_id: ActionList identifier (e.g., AL-001)
        service: ActionList service instance

    Returns:
        ActionList details

    Raises:
        404: ActionList not found
    """
    result = await service.get(list_id)

    match result:
        case Ok(action_list):
            return action_list
        case Err(error):
            raise error


@router.patch("/action-lists/{list_id}", response_model=ActionListResponse)
async def update_action_list(
    list_id: str,
    request: ActionListUpdateRequest,
    service: ActionListService = Depends(get_action_list_service),
) -> ActionListResponse:
    """Update action list with partial fields.

    Args:
        list_id: ActionList identifier
        request: Update request with optional fields
        service: ActionList service instance

    Returns:
        Updated action list

    Raises:
        404: ActionList not found
        422: Validation error
    """
    result = await service.update(list_id, request)

    match result:
        case Ok(action_list):
            return action_list
        case Err(error):
            raise error


@router.delete("/action-lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action_list(
    list_id: str,
    service: ActionListService = Depends(get_action_list_service),
) -> JSONResponse:
    """Delete action list by ID.

    Args:
        list_id: ActionList identifier
        service: ActionList service instance

    Returns:
        No content

    Raises:
        404: ActionList not found
    """
    result = await service.delete(list_id)

    match result:
        case Ok(_):
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        case Err(error):
            raise error


@router.get("/action-lists", response_model=list[ActionListResponse])
async def list_action_lists(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ActionListService = Depends(get_action_list_service),
) -> list[ActionListResponse]:
    """List action lists with pagination.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: ActionList service instance

    Returns:
        List of action lists
    """
    result = await service.list(limit=limit, offset=offset)

    match result:
        case Ok(action_lists):
            return action_lists
        case Err(error):
            raise error
