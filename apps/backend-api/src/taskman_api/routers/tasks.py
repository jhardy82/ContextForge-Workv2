"""
Tasks API Router
CRUD operations for task management.
Uses Service Layer for business logic and validation.
"""

import structlog
from fastapi import APIRouter, HTTPException, Query
from fastapi import status as http_status

from taskman_api.core.enums import TaskStatus
from taskman_api.core.errors import AppError, ConflictError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import TaskSvc
from taskman_api.schemas import TaskCreate, TaskList, TaskResponse, TaskUpdate

logger = structlog.get_logger()

# Create router
router = APIRouter()


# ============================================================================
# Endpoints (Service Layer Pattern)
# ============================================================================
@router.get("", response_model=TaskList)
async def list_tasks(
    service: TaskSvc,
    status: str | None = Query(None, description="Filter by status"),
    priority: str | None = Query(None, description="Filter by priority"),
    sprint_id: str | None = Query(None, description="Filter by sprint"),
    project_id: str | None = Query(None, description="Filter by project"),
    assignee: str | None = Query(None, description="Filter by assignee"),
    owner: str | None = Query(None, description="Filter by owner"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskList:
    """
    List all tasks with optional filtering and pagination.
    """
    offset = (page - 1) * per_page

    status_enum = None
    if status:
        try:
            status_enum = TaskStatus(status)
        except ValueError:
            pass

    # Priority ... simplified for now, assuming valid strings
    from taskman_api.core.enums import Priority

    priority_enum = None
    if priority:
        try:
            priority_enum = Priority(priority)
        except ValueError:
            pass

    # Call service
    result = await service.search(
        status=status_enum,
        priority=priority_enum,
        project_id=project_id,
        sprint_id=sprint_id,
        assignee=assignee,
        owner=owner,
        limit=per_page,
        offset=offset,
    )

    match result:
        case Ok((tasks, total)):
            logger.info("tasks_listed", count=len(tasks), total=total, page=page)
            return TaskList(
                tasks=tasks,  # Tasks are already TaskResponse objects
                total=total,
                page=page,
                per_page=per_page,
                has_more=offset + per_page < total,
            )
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("", response_model=TaskResponse, status_code=http_status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, service: TaskSvc) -> TaskResponse:
    """
    Create a new task.
    """
    result = await service.create(task)

    match result:
        case Ok(created):
            logger.info("task_created", task_id=str(created.id), title=created.title)
            return created
        case Err(ConflictError() as e):
            raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=e.message)
        case Err(AppError() as e):
            # Check if this is a wrapped database integrity error
            error_details = str(e) or e.message
            if "UNIQUE constraint" in error_details or "Duplicate" in error_details:
                raise HTTPException(
                    status_code=http_status.HTTP_409_CONFLICT,
                    detail=f"Task with this ID already exists: {error_details}",
                )
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, service: TaskSvc) -> TaskResponse:
    """
    Get a specific task by ID.
    """
    result = await service.get(task_id)

    match result:
        case Ok(task):
            logger.info("task_retrieved", task_id=task_id)
            return task
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.patch("/{task_id}", response_model=TaskResponse)
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskUpdate, service: TaskSvc) -> TaskResponse:
    """
    Update an existing task.
    """
    result = await service.update(task_id, task_update)

    match result:
        case Ok(updated):
            logger.info("task_updated", task_id=task_id)
            return updated
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(ValidationError() as e):
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.delete("/{task_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, service: TaskSvc) -> None:
    """
    Delete a task.
    """
    result = await service.delete(task_id)

    match result:
        case Ok(_):
            logger.info("task_deleted", task_id=task_id)
            return
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: str, service: TaskSvc) -> TaskResponse:
    """
    Mark a task as complete.
    Uses change_status to validate transition.
    """
    result = await service.change_status(task_id, new_status=TaskStatus.DONE)

    match result:
        case Ok(updated):
            logger.info("task_completed", task_id=task_id)
            return updated
        case Err(NotFoundError() as e):
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=e.message)
        case Err(ValidationError() as e):
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
            )
        case Err(error):
            raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(error))
