"""Sprint API endpoints.

Provides 6 REST endpoints for sprint management.
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from taskman_api.api.deps import get_sprint_service
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.sprint import (
    SprintCreateRequest,
    SprintResponse,
    SprintUpdateRequest,
)
from taskman_api.services.sprint_service import SprintService

router = APIRouter()


@router.post(
    "/sprints", status_code=status.HTTP_201_CREATED, response_model=SprintResponse
)
async def create_sprint(
    request: SprintCreateRequest,
    service: SprintService = Depends(get_sprint_service),
) -> SprintResponse:
    """Create a new sprint.

    Args:
        request: Sprint creation request with all required fields
        service: Sprint service instance

    Returns:
        Created sprint

    Raises:
        409: Sprint with ID already exists
        422: Validation error
    """
    result = await service.create(request)

    match result:
        case Ok(sprint):
            return sprint
        case Err(error):
            raise error


@router.get("/sprints/{sprint_id}", response_model=SprintResponse)
async def get_sprint(
    sprint_id: str,
    service: SprintService = Depends(get_sprint_service),
) -> SprintResponse:
    """Get sprint by ID.

    Args:
        sprint_id: Sprint identifier (e.g., S-2025-01)
        service: Sprint service instance

    Returns:
        Sprint details

    Raises:
        404: Sprint not found
    """
    result = await service.get(sprint_id)

    match result:
        case Ok(sprint):
            return sprint
        case Err(error):
            raise error


@router.patch("/sprints/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: str,
    request: SprintUpdateRequest,
    service: SprintService = Depends(get_sprint_service),
) -> SprintResponse:
    """Update sprint with partial fields.

    Args:
        sprint_id: Sprint identifier
        request: Update request with optional fields
        service: Sprint service instance

    Returns:
        Updated sprint

    Raises:
        404: Sprint not found
        422: Validation error
    """
    result = await service.update(sprint_id, request)

    match result:
        case Ok(sprint):
            return sprint
        case Err(error):
            raise error


@router.delete("/sprints/{sprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sprint(
    sprint_id: str,
    service: SprintService = Depends(get_sprint_service),
) -> JSONResponse:
    """Delete sprint by ID.

    Args:
        sprint_id: Sprint identifier
        service: Sprint service instance

    Returns:
        No content

    Raises:
        404: Sprint not found
    """
    result = await service.delete(sprint_id)

    match result:
        case Ok(_):
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        case Err(error):
            raise error


@router.get("/sprints", response_model=list[SprintResponse])
async def list_sprints(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: SprintService = Depends(get_sprint_service),
) -> list[SprintResponse]:
    """List sprints with pagination.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Sprint service instance

    Returns:
        List of sprints
    """
    result = await service.list(limit=limit, offset=offset)

    match result:
        case Ok(sprints):
            return sprints
        case Err(error):
            raise error


@router.get("/sprints/{sprint_id}/burndown")
async def get_sprint_burndown(
    sprint_id: str,
    service: SprintService = Depends(get_sprint_service),
) -> dict[str, object]:
    """Get sprint burndown chart data.

    Calculates:
    - Total/remaining/completed points
    - Days total/elapsed/remaining
    - Ideal vs actual burndown rate
    - On-track indicator

    Args:
        sprint_id: Sprint identifier
        service: Sprint service instance

    Returns:
        Burndown chart data dict

    Raises:
        404: Sprint not found
    """
    result = await service.get_burndown(sprint_id)

    match result:
        case Ok(burndown):
            return burndown
        case Err(error):
            raise error
