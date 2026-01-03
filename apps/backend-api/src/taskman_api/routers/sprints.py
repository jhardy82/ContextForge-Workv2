"""
Sprints API Router
CRUD operations for sprint management.
Uses Service Layer for business logic and validation.
"""

import structlog
from fastapi import APIRouter, HTTPException, Query
from fastapi import status as http_status

from taskman_api.core.enums import SprintStatus
from taskman_api.core.errors import AppError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import SprintSvc
from taskman_api.schemas import (
    SprintCreate,
    SprintList,
    SprintProgress,
    SprintResponse,
    SprintUpdate,
)

logger = structlog.get_logger()

router = APIRouter()


# ============================================================================
# Endpoints (Service Layer Pattern)
# ============================================================================
@router.get("", response_model=SprintList)
async def list_sprints(
    service: SprintSvc,
    status: str | None = Query(None, description="Filter by status"),
    project_id: str | None = Query(None, description="Filter by project"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> SprintList:
    """
    List all sprints with optional filtering and pagination.
    """
    offset = (page - 1) * per_page

    status_enum = None
    if status:
        try:
            status_enum = SprintStatus(status)
        except ValueError:
            pass

    # Call service
    result = await service.search(
        status=status_enum,
        project_id=project_id,
        limit=per_page,
        offset=offset,
    )

    match result:
        case Ok((sprints, total)):
            logger.info("sprints_listed", count=len(sprints), total=total, page=page)
            return SprintList(
                sprints=sprints,
                total=total,
                page=page,
                per_page=per_page,
                has_more=offset + per_page < total,
            )
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("", response_model=SprintResponse, status_code=http_status.HTTP_201_CREATED)
async def create_sprint(sprint: SprintCreate, service: SprintSvc) -> SprintResponse:
    """
    Create a new sprint.
    """
    result = await service.create(sprint)

    match result:
        case Ok(created):
            logger.info("sprint_created", sprint_id=created.id, name=created.name)
            return created
        case Err(NotFoundError() as e):
            # Project not found usually
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(AppError() as e):
            error_details = str(e) or e.message
            if "UNIQUE constraint" in error_details or "Duplicate" in error_details:
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail=f"Sprint with this ID already exists: {error_details}",
                )
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/{sprint_id}", response_model=SprintResponse)
async def get_sprint(sprint_id: str, service: SprintSvc) -> SprintResponse:
    """
    Get a specific sprint by ID.
    """
    result = await service.get(sprint_id)

    match result:
        case Ok(sprint):
            logger.info("sprint_retrieved", sprint_id=sprint_id)
            return sprint
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.get("/{sprint_id}/progress", response_model=SprintProgress)
async def get_sprint_progress(sprint_id: str, service: SprintSvc) -> SprintProgress:
    """
    Get sprint progress report.
    """
    result = await service.get_progress(sprint_id)

    match result:
        case Ok(progress):
            logger.info("sprint_progress_retrieved", sprint_id=sprint_id)
            return progress
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.put("/{sprint_id}", response_model=SprintResponse)
async def update_sprint(
    sprint_id: str, sprint_update: SprintUpdate, service: SprintSvc
) -> SprintResponse:
    """
    Update an existing sprint.
    """
    result = await service.update(sprint_id, sprint_update)

    match result:
        case Ok(updated):
            logger.info("sprint_updated", sprint_id=sprint_id)
            return updated
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(ValidationError() as e):
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.delete("/{sprint_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_sprint(sprint_id: str, service: SprintSvc) -> None:
    """
    Delete a sprint.
    """
    result = await service.delete(sprint_id)

    match result:
        case Ok(_):
            logger.info("sprint_deleted", sprint_id=sprint_id)
            return
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/{sprint_id}/start", response_model=SprintResponse)
async def start_sprint(sprint_id: str, service: SprintSvc) -> SprintResponse:
    """
    Start a sprint (set status to active).
    """
    result = await service.change_status(sprint_id, SprintStatus.ACTIVE)

    match result:
        case Ok(updated):
            logger.info("sprint_started", sprint_id=sprint_id)
            return updated
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/{sprint_id}/complete", response_model=SprintResponse)
async def complete_sprint(sprint_id: str, service: SprintSvc) -> SprintResponse:
    """
    Complete a sprint.
    """
    result = await service.change_status(sprint_id, SprintStatus.COMPLETED)

    match result:
        case Ok(updated):
            logger.info("sprint_completed", sprint_id=sprint_id)
            return updated
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))
