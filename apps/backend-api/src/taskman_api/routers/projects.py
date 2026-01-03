"""
Projects API Router
CRUD operations for project management.
Uses Service Layer for business logic and validation.
"""

import structlog
from fastapi import APIRouter, HTTPException, Query
from fastapi import status as http_status

from taskman_api.core.enums import ProjectStatus
from taskman_api.core.errors import AppError, ConflictError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import ProjectSvc
from taskman_api.schemas import ProjectCreate, ProjectList, ProjectResponse, ProjectUpdate

logger = structlog.get_logger()

router = APIRouter()


# ============================================================================
# Endpoints (Service Layer Pattern)
# ============================================================================
@router.get("", response_model=ProjectList)
async def list_projects(
    service: ProjectSvc,
    status: str | None = Query(None, description="Filter by status"),
    owner: str | None = Query(None, description="Filter by owner"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ProjectList:
    """
    List all projects with optional filtering and pagination.
    """
    offset = (page - 1) * per_page

    status_enum = None
    if status:
        try:
            status_enum = ProjectStatus(status)
        except ValueError:
            pass

    # Call service
    result = await service.search(
        status=status_enum,
        owner=owner,
        limit=per_page,
        offset=offset,
    )

    match result:
        case Ok((projects, total)):
            logger.info("projects_listed", count=len(projects), total=total, page=page)
            return ProjectList(
                projects=projects,
                total=total,
                page=page,
                per_page=per_page,
                has_more=offset + per_page < total,
            )
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("", response_model=ProjectResponse, status_code=http_status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, service: ProjectSvc) -> ProjectResponse:
    """
    Create a new project.
    """
    result = await service.create(project)

    match result:
        case Ok(created):
            logger.info("project_created", project_id=created.id, name=created.name)
            return created
        case Err(ConflictError() as e):
            raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=e.message)
        case Err(AppError() as e):
            # Check if this is a wrapped database integrity error
            error_details = str(e) or e.message
            if "UNIQUE constraint" in error_details or "Duplicate" in error_details:
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail=f"Project with this ID already exists: {error_details}",
                )
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, service: ProjectSvc) -> ProjectResponse:
    """
    Get a specific project by ID.
    """
    result = await service.get(project_id)

    match result:
        case Ok(project):
            logger.info("project_retrieved", project_id=project_id)
            return project
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str, project_update: ProjectUpdate, service: ProjectSvc
) -> ProjectResponse:
    """
    Update an existing project.
    """
    result = await service.update(project_id, project_update)

    match result:
        case Ok(updated):
            logger.info("project_updated", project_id=project_id)
            return updated
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(ValidationError() as e):
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.delete("/{project_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, service: ProjectSvc) -> None:
    """
    Delete a project.
    """
    result = await service.delete(project_id)

    match result:
        case Ok(_):
            logger.info("project_deleted", project_id=project_id)
            return
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))
