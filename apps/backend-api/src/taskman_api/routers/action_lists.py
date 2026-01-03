"""
ActionList API Router
CRUD operations for action list management with task association.
Uses Service Layer for business logic and validation.
"""

import structlog
from fastapi import APIRouter, HTTPException, Query
from fastapi import status as http_status

from taskman_api.dependencies import ActionListSvc
from taskman_api.schemas.action_list import (
    ActionListAddItemRequest,
    ActionListCollection,
    ActionListCreate,
    ActionListResponse,
    ActionListUpdate,
    ReorderItemsRequest,
)

logger = structlog.get_logger()

# Create router
router = APIRouter()


# ============================================================================
# Endpoints (Service Layer Pattern)
# ============================================================================
@router.post(
    "",
    response_model=ActionListResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Create new action list",
    description="""
    Creates a new action list with the specified title, description, and optional metadata.

    The action list will be created with 'active' status by default. You can associate
    it with a project and sprint, add tags, and include checklist items.

    **ContextForge Integration**: Supports geometry_shape, priority, due_date, and evidence_refs.

    Returns the created ActionList with generated timestamps.
    """,
    responses={
        201: {
            "description": "Action list created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "AL-backend-api-tasks",
                        "title": "Backend API Implementation",
                        "description": "Core API endpoints for TaskMan v2",
                        "status": "active",
                        "owner": "backend-team",
                        "tags": ["api", "backend", "sprint-1"],
                        "project_id": "PROJ-001",
                        "sprint_id": "SPRINT-2025-Q1",
                        "items": [
                            {"text": "Implement authentication", "completed": False, "order": 0}
                        ],
                        "priority": "high",
                        "due_date": "2025-12-31T23:59:59Z",
                        "created_at": "2025-12-28T10:30:00Z",
                        "updated_at": "2025-12-28T10:30:00Z",
                    }
                }
            },
        },
        400: {"description": "Invalid request data - validation error or business rule violation"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        422: {"description": "Unprocessable entity - semantic validation failure"},
        500: {"description": "Internal server error - unexpected system failure"},
    },
    tags=["Action Lists"],
)
async def create_action_list(
    data: ActionListCreate,
    service: ActionListSvc,
) -> ActionListResponse:
    """Create new action list endpoint handler."""
    result = await service.create_action_list(
        name=data.title,
        description=data.description or "",
        owner=data.owner or "system",
        project_id=data.project_id,
        sprint_id=data.sprint_id,
        tags=data.tags,
        priority=data.priority,
        due_date=data.due_date,
        items=data.items,
    )

    if result.is_failure:
        logger.error("action_list_create_failed", error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    action_list = result.value
    logger.info("action_list_created", list_id=action_list.id, name=action_list.title)

    return ActionListResponse.model_validate(action_list.model_dump())


@router.get(
    "",
    response_model=ActionListCollection,
    summary="List action lists",
    description="""
    Retrieve a paginated collection of action lists with optional filtering.

    **Filtering Options**:
    - `status`: Filter by action list status (active, completed, archived)
    - `owner`: Filter by owner name (exact match)
    - `project_id`: Filter by associated project
    - `sprint_id`: Filter by associated sprint

    **Pagination**:
    - Default: 20 items per page
    - Maximum: 100 items per page
    - Use `page` parameter to navigate through results

    Returns total count for building pagination controls.
    """,
    responses={
        200: {
            "description": "Action lists retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "action_lists": [
                            {
                                "id": "AL-backend-tasks",
                                "title": "Backend API Tasks",
                                "description": "Core API implementation",
                                "status": "active",
                                "owner": "backend-team",
                                "tags": ["api", "backend"],
                                "created_at": "2025-12-28T10:00:00Z",
                                "updated_at": "2025-12-28T10:30:00Z",
                            }
                        ],
                        "total": 45,
                        "page": 1,
                        "per_page": 20,
                        "has_more": True,
                    }
                }
            },
        },
        400: {"description": "Invalid query parameters"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
async def list_action_lists(
    service: ActionListSvc,
    status: str | None = Query(None, description="Filter by status (active, completed, archived)"),
    owner: str | None = Query(None, description="Filter by owner name (exact match)"),
    project_id: str | None = Query(None, description="Filter by associated project ID"),
    sprint_id: str | None = Query(None, description="Filter by associated sprint ID"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
) -> ActionListCollection:
    """List action lists endpoint handler."""
    offset = (page - 1) * per_page

    result = await service.list_action_lists(
        status=status,
        owner=owner,
        project_id=project_id,
        sprint_id=sprint_id,
        limit=per_page,
        offset=offset,
    )

    if result.is_failure:
        logger.error("action_lists_list_failed", error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    action_lists, total = result.value
    logger.info("action_lists_listed", count=len(action_lists), total=total, page=page)

    return ActionListCollection(
        action_lists=[ActionListResponse.model_validate(al.model_dump()) for al in action_lists],
        total=total,
        page=page,
        per_page=per_page,
        has_more=offset + per_page < total,
    )


@router.get(
    "/{list_id}",
    response_model=ActionListResponse,
    summary="Get action list by ID",
    description="""
    Retrieve a specific action list by its unique identifier.

    Returns complete action list details including:
    - Core metadata (title, description, status, owner)
    - Project and sprint associations
    - Tags and checklist items
    - ContextForge fields (geometry_shape, priority, due_date)
    - Evidence references and extra metadata
    - Timestamps (created_at, updated_at, completed_at)

    **Use Case**: Fetch full details before updating or displaying to user.
    """,
    responses={
        200: {
            "description": "Action list retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "AL-backend-tasks",
                        "title": "Backend API Implementation",
                        "description": "Core endpoints and authentication",
                        "status": "active",
                        "owner": "backend-team",
                        "tags": ["api", "backend", "priority"],
                        "project_id": "PROJ-001",
                        "sprint_id": "SPRINT-2025-Q1",
                        "items": [
                            {"text": "Implement JWT auth", "completed": True, "order": 0},
                            {"text": "Create CRUD endpoints", "completed": False, "order": 1},
                        ],
                        "geometry_shape": "rectangle",
                        "priority": "high",
                        "due_date": "2025-12-31T23:59:59Z",
                        "evidence_refs": ["EVD-001", "EVD-002"],
                        "extra_metadata": {"velocity": 8, "confidence": 0.85},
                        "notes": "Critical path items",
                        "created_at": "2025-12-28T10:00:00Z",
                        "updated_at": "2025-12-28T15:30:00Z",
                        "completed_at": None,
                    }
                }
            },
        },
        404: {"description": "Action list not found - invalid or deleted ID"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
async def get_action_list(
    list_id: str,
    service: ActionListSvc,
) -> ActionListResponse:
    """Get action list by ID endpoint handler."""
    result = await service.get_action_list(list_id)

    if result.is_failure:
        logger.error("action_list_get_failed", list_id=list_id, error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"ActionList not found: {list_id}",
        )

    action_list = result.value
    if action_list is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"ActionList not found: {list_id}",
        )

    logger.info("action_list_retrieved", list_id=list_id)
    return ActionListResponse.model_validate(action_list.model_dump())


@router.put(
    "/{list_id}",
    response_model=ActionListResponse,
    summary="Update action list (full/partial)",
    description="""
    Update an existing action list with new values.

    **Partial Updates Supported**: Only fields included in the request body are modified.
    All other fields remain unchanged.

    **Updatable Fields**:
    - Core: title, description, status, owner
    - Associations: project_id, sprint_id, tags
    - Items: checklist items array
    - ContextForge: geometry_shape, priority, due_date
    - Metadata: evidence_refs, extra_metadata, notes
    - Completion: completed_at timestamp

    The `updated_at` timestamp is automatically set to the current time.

    **Use Case**: Modify action list details without recreating.
    """,
    responses={
        200: {
            "description": "Action list updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "AL-backend-tasks",
                        "title": "Backend API Implementation (Updated)",
                        "description": "Core endpoints, auth, and documentation",
                        "status": "active",
                        "owner": "backend-team",
                        "tags": ["api", "backend", "priority", "docs"],
                        "updated_at": "2025-12-28T16:45:00Z",
                    }
                }
            },
        },
        400: {"description": "Invalid request data - validation error"},
        404: {"description": "Action list not found"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        422: {"description": "Unprocessable entity - semantic validation failure"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
@router.patch(
    "/{list_id}",
    response_model=ActionListResponse,
    summary="Update action list (partial)",
    description="Alias for PUT. Supports partial updates - only provided fields are modified.",
    responses={
        200: {"description": "Action list updated successfully"},
        400: {"description": "Invalid request data"},
        404: {"description": "Action list not found"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
async def update_action_list(
    list_id: str,
    data: ActionListUpdate,
    service: ActionListSvc,
) -> ActionListResponse:
    """Update action list endpoint handler (PUT/PATCH)."""
    # Build update dictionary from provided fields
    updates = data.model_dump(exclude_unset=True)

    # Map 'title' to 'name' if present
    if "title" in updates:
        updates["name"] = updates.pop("title")

    result = await service.update_action_list(list_id, **updates)

    if result.is_failure:
        logger.error("action_list_update_failed", list_id=list_id, error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    action_list = result.value
    logger.info("action_list_updated", list_id=list_id)
    return ActionListResponse.model_validate(action_list.model_dump())


@router.delete(
    "/{list_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Delete action list",
    description="""
    Permanently delete an action list by ID.

    **Warning**: This action cannot be undone. The action list and all its associations
    (task links, metadata) will be permanently removed.

    **Returns**: HTTP 204 No Content on successful deletion.

    **Use Case**: Remove obsolete or duplicate action lists. Consider archiving
    (setting status='archived') instead of deletion for audit trail.
    """,
    responses={
        204: {"description": "Action list deleted successfully (no content returned)"},
        404: {"description": "Action list not found - may already be deleted"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
async def delete_action_list(
    list_id: str,
    service: ActionListSvc,
) -> None:
    """Delete action list endpoint handler."""
    result = await service.delete_action_list(list_id)

    if result.is_failure:
        logger.error("action_list_delete_failed", list_id=list_id, error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(result.error),
        )

    logger.info("action_list_deleted", list_id=list_id)


@router.get(
    "/{list_id}/tasks",
    response_model=list[str],
    summary="Get action list tasks",
    description="""
    Retrieve all task IDs associated with a specific action list.

    Returns an ordered array of task UUIDs linked to this action list.
    Task IDs are returned in the order they were added.

    **Use Case**: Fetch task IDs to query full task details from tasks endpoint.

    **Example**: Use returned IDs to fetch tasks via `GET /api/v1/tasks/{task_id}`
    """,
    responses={
        200: {
            "description": "Task IDs retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        "550e8400-e29b-41d4-a716-446655440000",
                        "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                        "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                    ]
                }
            },
        },
        404: {"description": "Action list not found"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
async def get_action_list_tasks(
    list_id: str,
    service: ActionListSvc,
) -> list[str]:
    """Get action list tasks endpoint handler."""
    result = await service.get_tasks_for_action_list(list_id)

    if result.is_failure:
        logger.error("action_list_tasks_get_failed", list_id=list_id, error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(result.error),
        )

    task_ids = result.value
    logger.info("action_list_tasks_retrieved", list_id=list_id, count=len(task_ids))
    return task_ids


@router.post(
    "/{list_id}/tasks",
    response_model=ActionListResponse,
    summary="Add task to action list",
    description="""
    Associate a task with an action list by adding the task ID.

    **Idempotent Operation**: If the task is already associated with the list,
    the operation succeeds without error and returns the existing state.

    **Use Case**: Link tasks to action lists for grouping and tracking.

    **Note**: The task must exist in the tasks table. Invalid task IDs will
    be rejected with a 400 error.
    """,
    responses={
        200: {
            "description": "Task added successfully (or already exists)",
            "content": {
                "application/json": {
                    "example": {
                        "id": "AL-backend-tasks",
                        "title": "Backend API Implementation",
                        "items": [
                            {"text": "Existing task 1", "completed": False},
                            {"text": "Newly added task", "completed": False},
                        ],
                        "updated_at": "2025-12-28T17:00:00Z",
                    }
                }
            },
        },
        400: {"description": "Invalid task ID or task does not exist"},
        404: {"description": "Action list not found"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
async def add_task_to_action_list(
    list_id: str,
    service: ActionListSvc,
    task_id: str = Query(..., description="UUID of the task to add to the action list"),
) -> ActionListResponse:
    """Add task to action list endpoint handler."""
    result = await service.add_task_to_action_list(list_id, task_id)

    if result.is_failure:
        logger.error(
            "action_list_task_add_failed",
            list_id=list_id,
            task_id=task_id,
            error=result.error,
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    action_list = result.value
    logger.info("task_added_to_action_list", list_id=list_id, task_id=task_id)
    return ActionListResponse.model_validate(action_list.model_dump())


@router.delete(
    "/{list_id}/tasks/{task_id}",
    response_model=ActionListResponse,
    summary="Remove task from action list",
    description="""
    Disassociate a task from an action list by removing the task ID.

    **Idempotent Operation**: If the task is not currently associated with the list,
    the operation succeeds without error and returns the existing state.

    **Use Case**: Unlink tasks from action lists when reorganizing or cleaning up.

    **Note**: This does NOT delete the task itself - only removes the association.
    The task remains in the tasks table.
    """,
    responses={
        200: {
            "description": "Task removed successfully (or was not associated)",
            "content": {
                "application/json": {
                    "example": {
                        "id": "AL-backend-tasks",
                        "title": "Backend API Implementation",
                        "items": [{"text": "Remaining task 1", "completed": False}],
                        "updated_at": "2025-12-28T17:15:00Z",
                    }
                }
            },
        },
        400: {"description": "Invalid request parameters"},
        404: {"description": "Action list not found"},
        401: {"description": "Unauthorized - missing or invalid JWT token"},
        500: {"description": "Internal server error"},
    },
    tags=["Action Lists"],
)
async def remove_task_from_action_list(
    list_id: str,
    task_id: str,
    service: ActionListSvc,
) -> ActionListResponse:
    """Remove task from action list endpoint handler."""
    result = await service.remove_task_from_action_list(list_id, task_id)

    if result.is_failure:
        logger.error(
            "action_list_task_remove_failed",
            list_id=list_id,
            task_id=task_id,
            error=result.error,
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    action_list = result.value
    logger.info("task_removed_from_action_list", list_id=list_id, task_id=task_id)
    return ActionListResponse.model_validate(action_list.model_dump())


@router.post(
    "/{list_id}/items",
    response_model=ActionListResponse,
    summary="Add text item to action list",
    description="Add a manual text item to the action list.",
    tags=["Action Lists"],
)
async def add_item_to_action_list(
    list_id: str,
    data: ActionListAddItemRequest,
    service: ActionListSvc,
) -> ActionListResponse:
    """Add text item to action list endpoint handler."""
    result = await service.add_item(list_id, data)

    if result.is_failure:
        logger.error("action_list_item_add_failed", list_id=list_id, error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    action_list = result.value
    logger.info("item_added_to_action_list", list_id=list_id)
    return ActionListResponse.model_validate(action_list.model_dump())


@router.delete(
    "/{list_id}/items/{item_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Remove item from action list",
    description="Remove an item (text or ID) from the action list.",
    tags=["Action Lists"],
)
async def remove_item_from_action_list(
    list_id: str,
    item_id: str,
    service: ActionListSvc,
) -> None:
    """Remove item from action list endpoint handler."""
    result = await service.remove_item(list_id, item_id)

    if result.is_failure:
        logger.error(
            "action_list_item_remove_failed", list_id=list_id, item_id=item_id, error=result.error
        )
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    logger.info("item_removed_from_action_list", list_id=list_id, item_id=item_id)


@router.patch(
    "/{list_id}/items/reorder",
    response_model=ActionListResponse,
    summary="Reorder action list items",
    description="Reorder the items in the action list.",
    tags=["Action Lists"],
)
async def reorder_action_list_items(
    list_id: str,
    data: ReorderItemsRequest,
    service: ActionListSvc,
) -> ActionListResponse:
    """Reorder action list items endpoint handler."""
    result = await service.reorder_items(list_id, data)

    if result.is_failure:
        logger.error("action_list_reorder_failed", list_id=list_id, error=result.error)
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=str(result.error),
        )

    action_list = result.value
    logger.info("action_list_items_reordered", list_id=list_id)
    return ActionListResponse.model_validate(action_list.model_dump())
