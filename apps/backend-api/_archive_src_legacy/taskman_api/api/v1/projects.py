"""Project API endpoints.

Provides 6 REST endpoints for project management.
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from taskman_api.api.deps import get_project_service
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from taskman_api.services.project_service import ProjectService

router = APIRouter()


@router.post(
    "/projects", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse
)
async def create_project(
    request: ProjectCreateRequest,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Create a new project.

    Args:
        request: Project creation request with all required fields
        service: Project service instance

    Returns:
        Created project

    Raises:
        409: Project with ID already exists
        422: Validation error
    """
    result = await service.create(request)

    match result:
        case Ok(project):
            return project
        case Err(error):
            raise error


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Get project by ID.

    Args:
        project_id: Project identifier (e.g., P-TASKMAN)
        service: Project service instance

    Returns:
        Project details

    Raises:
        404: Project not found
    """
    result = await service.get(project_id)

    match result:
        case Ok(project):
            return project
        case Err(error):
            raise error


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    """Update project with partial fields.

    Args:
        project_id: Project identifier
        request: Update request with optional fields
        service: Project service instance

    Returns:
        Updated project

    Raises:
        404: Project not found
        422: Validation error
    """
    result = await service.update(project_id, request)

    match result:
        case Ok(project):
            return project
        case Err(error):
            raise error


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
) -> JSONResponse:
    """Delete project by ID.

    Args:
        project_id: Project identifier
        service: Project service instance

    Returns:
        No content

    Raises:
        404: Project not found
    """
    result = await service.delete(project_id)

    match result:
        case Ok(_):
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        case Err(error):
            raise error


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectResponse]:
    """List projects with pagination.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Project service instance

    Returns:
        List of projects
    """
    result = await service.list(limit=limit, offset=offset)

    match result:
        case Ok(projects):
            return projects
        case Err(error):
            raise error


@router.get("/projects/{project_id}/metrics")
async def get_project_metrics(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
) -> dict[str, object]:
    """Get project metrics and health status.

    Calculates:
    - Total task count
    - Tasks by status breakdown
    - Completion percentage
    - Blocked percentage
    - Health status (green/yellow/red)

    Args:
        project_id: Project identifier
        service: Project service instance

    Returns:
        Project metrics dict

    Raises:
        404: Project not found
    """
    result = await service.get_metrics(project_id)

    match result:
        case Ok(metrics):
            return metrics
        case Err(error):
            raise error
