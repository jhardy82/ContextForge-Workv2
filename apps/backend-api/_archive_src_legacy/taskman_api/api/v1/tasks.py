"""Task API endpoints.

Provides 10 REST endpoints for task management.
"""


from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from taskman_api.api.deps import get_task_service
from taskman_api.core.enums import Priority, TaskStatus
from taskman_api.core.result import Err, Ok
from taskman_api.schemas.task import TaskCreateRequest, TaskResponse, TaskUpdateRequest
from taskman_api.services.task_service import TaskService

router = APIRouter()


@router.post("/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    request: TaskCreateRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Create a new task.

    Args:
        request: Task creation request with all required fields
        service: Task service instance

    Returns:
        Created task

    Raises:
        409: Task with ID already exists
        422: Validation error
    """
    result = await service.create(request)

    match result:
        case Ok(task):
            return task
        case Err(error):
            raise error


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Get task by ID.

    Args:
        task_id: Task identifier (e.g., T-001)
        service: Task service instance

    Returns:
        Task details

    Raises:
        404: Task not found
    """
    result = await service.get(task_id)

    match result:
        case Ok(task):
            return task
        case Err(error):
            raise error


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: TaskUpdateRequest,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Update task with partial fields.

    Args:
        task_id: Task identifier
        request: Update request with optional fields
        service: Task service instance

    Returns:
        Updated task

    Raises:
        404: Task not found
        422: Validation error
    """
    result = await service.update(task_id, request)

    match result:
        case Ok(task):
            return task
        case Err(error):
            raise error


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
) -> JSONResponse:
    """Delete task by ID.

    Args:
        task_id: Task identifier
        service: Task service instance

    Returns:
        No content

    Raises:
        404: Task not found
    """
    result = await service.delete(task_id)

    match result:
        case Ok(_):
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        case Err(error):
            raise error


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    """List tasks with pagination.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Task service instance

    Returns:
        List of tasks
    """
    result = await service.list(limit=limit, offset=offset)

    match result:
        case Ok(tasks):
            return tasks
        case Err(error):
            raise error


@router.post("/tasks/{task_id}/status", response_model=TaskResponse)
async def change_task_status(
    task_id: str,
    new_status: TaskStatus,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Change task status with validation.

    Args:
        task_id: Task identifier
        status: New status to set
        service: Task service instance

    Returns:
        Updated task

    Raises:
        404: Task not found
        422: Invalid status transition
    """
    result = await service.change_status(task_id, new_status)

    match result:
        case Ok(task):
            return task
        case Err(error):
            raise error


@router.post("/tasks/{task_id}/assign-sprint", response_model=TaskResponse)
async def assign_task_to_sprint(
    task_id: str,
    sprint_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Assign task to sprint.

    Args:
        task_id: Task identifier
        sprint_id: Sprint identifier
        service: Task service instance

    Returns:
        Updated task

    Raises:
        404: Task not found
    """
    result = await service.assign_to_sprint(task_id, sprint_id)

    match result:
        case Ok(task):
            return task
        case Err(error):
            raise error


@router.post("/tasks/{task_id}/assign-project", response_model=TaskResponse)
async def assign_task_to_project(
    task_id: str,
    project_id: str,
    service: TaskService = Depends(get_task_service),
) -> TaskResponse:
    """Assign task to project.

    Args:
        task_id: Task identifier
        project_id: Project identifier
        service: Task service instance

    Returns:
        Updated task

    Raises:
        404: Task not found
    """
    result = await service.assign_to_project(task_id, project_id)

    match result:
        case Ok(task):
            return task
        case Err(error):
            raise error


@router.get("/tasks/search", response_model=list[TaskResponse])
async def search_tasks(
    status: TaskStatus | None = None,
    priority: Priority | None = None,
    owner: str | None = None,
    project_id: str | None = None,
    sprint_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    """Search tasks with filters.

    Args:
        status: Filter by status
        priority: Filter by priority
        owner: Filter by owner username
        project_id: Filter by project
        sprint_id: Filter by sprint
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Task service instance

    Returns:
        Filtered list of tasks
    """
    result = await service.search(
        status=status,
        priority=priority,
        owner=owner,
        project_id=project_id,
        sprint_id=sprint_id,
        limit=limit,
        offset=offset,
    )

    match result:
        case Ok(tasks):
            return tasks
        case Err(error):
            raise error


@router.get("/tasks/high-priority", response_model=list[TaskResponse])
async def get_high_priority_tasks(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> list[TaskResponse]:
    """Get high priority tasks (P0, P1).

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Task service instance

    Returns:
        List of high priority tasks
    """
    result = await service.get_high_priority_tasks(limit=limit, offset=offset)

    match result:
        case Ok(tasks):
            return tasks
        case Err(error):
            raise error
