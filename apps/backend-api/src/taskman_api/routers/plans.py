"""Plan API endpoints.

Provides REST endpoints for plan management.
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_plan_service
from taskman_api.schemas.plan import (
    PlanCreateRequest,
    PlanResponse,
    PlanStepInput,
    PlanUpdateRequest,
)
from taskman_api.services.plan_service import PlanService

router = APIRouter()


# =========================================================================
# Search and Queries (MUST come before parametric routes)
# =========================================================================


@router.get("/plans/search", response_model=list[PlanResponse])
async def search_plans(
    status: str | None = None,
    project_id: str | None = None,
    sprint_id: str | None = None,
    conversation_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: PlanService = Depends(get_plan_service),
):
    """Search plans with filters.

    Args:
        status: Filter by status
        project_id: Filter by project
        sprint_id: Filter by sprint
        conversation_id: Filter by conversation
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Plan service instance

    Returns:
        Filtered list of plans
    """
    result = await service.search(
        status=status,
        project_id=project_id,
        sprint_id=sprint_id,
        conversation_id=conversation_id,
        limit=limit,
        offset=offset,
    )

    match result:
        case Ok(plans):
            return plans
        case Err(error):
            raise error


@router.get("/plans/drafts", response_model=list[PlanResponse])
async def get_draft_plans(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: PlanService = Depends(get_plan_service),
):
    """Get all draft plans awaiting approval.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Plan service instance

    Returns:
        List of draft plans
    """
    result = await service.get_drafts(limit=limit, offset=offset)

    match result:
        case Ok(plans):
            return plans
        case Err(error):
            raise error


@router.get("/plans/in-progress", response_model=list[PlanResponse])
async def get_in_progress_plans(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: PlanService = Depends(get_plan_service),
):
    """Get all in-progress plans.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Plan service instance

    Returns:
        List of in-progress plans
    """
    result = await service.get_in_progress(limit=limit, offset=offset)

    match result:
        case Ok(plans):
            return plans
        case Err(error):
            raise error


@router.get("/plans/stalled", response_model=list[PlanResponse])
async def get_stalled_plans(
    days_inactive: int = Query(default=3, ge=1, le=30),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: PlanService = Depends(get_plan_service),
):
    """Get stalled plans (in_progress but not updated recently).

    Args:
        days_inactive: Days without update to consider stalled
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Plan service instance

    Returns:
        List of stalled plans
    """
    result = await service.get_stalled(
        days_inactive=days_inactive,
        limit=limit,
        offset=offset,
    )

    match result:
        case Ok(plans):
            return plans
        case Err(error):
            raise error


@router.get("/plans/stats")
async def get_plan_stats(
    service: PlanService = Depends(get_plan_service),
):
    """Get plan statistics.

    Args:
        service: Plan service instance

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
# Plan CRUD
# =========================================================================


@router.post(
    "/plans",
    status_code=status.HTTP_201_CREATED,
    response_model=PlanResponse,
)
async def create_plan(
    request: PlanCreateRequest,
    service: PlanService = Depends(get_plan_service),
):
    """Create a new plan.

    Args:
        request: Plan creation request
        service: Plan service instance

    Returns:
        Created plan

    Raises:
        409: Plan with ID already exists
        422: Validation error
    """
    result = await service.create(request)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: str,
    service: PlanService = Depends(get_plan_service),
):
    """Get plan by ID.

    Args:
        plan_id: Plan identifier
        service: Plan service instance

    Returns:
        Plan details

    Raises:
        404: Plan not found
    """
    result = await service.get(plan_id)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


@router.patch("/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    request: PlanUpdateRequest,
    service: PlanService = Depends(get_plan_service),
):
    """Update plan with partial fields.

    Args:
        plan_id: Plan identifier
        request: Update request with optional fields
        service: Plan service instance

    Returns:
        Updated plan

    Raises:
        404: Plan not found
        422: Validation error
    """
    result = await service.update(plan_id, request)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    service: PlanService = Depends(get_plan_service),
):
    """Delete plan by ID.

    Args:
        plan_id: Plan identifier
        service: Plan service instance

    Returns:
        No content

    Raises:
        404: Plan not found
    """
    result = await service.delete(plan_id)

    match result:
        case Ok(_):
            return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
        case Err(error):
            raise error


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: PlanService = Depends(get_plan_service),
):
    """List plans with pagination.

    Args:
        limit: Maximum results (1-1000, default: 100)
        offset: Results to skip (default: 0)
        service: Plan service instance

    Returns:
        List of plans
    """
    result = await service.list(limit=limit, offset=offset)

    match result:
        case Ok(plans):
            return plans
        case Err(error):
            raise error


# =========================================================================
# Plan Lifecycle Operations
# =========================================================================


@router.post("/plans/{plan_id}/approve", response_model=PlanResponse)
async def approve_plan(
    plan_id: str,
    service: PlanService = Depends(get_plan_service),
):
    """Approve a draft plan for execution.

    Args:
        plan_id: Plan identifier
        service: Plan service instance

    Returns:
        Updated plan

    Raises:
        404: Plan not found
        422: Plan is not in draft status
    """
    result = await service.approve(plan_id)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


@router.post("/plans/{plan_id}/start", response_model=PlanResponse)
async def start_plan(
    plan_id: str,
    service: PlanService = Depends(get_plan_service),
):
    """Start executing an approved plan.

    Args:
        plan_id: Plan identifier
        service: Plan service instance

    Returns:
        Updated plan

    Raises:
        404: Plan not found
        422: Plan is not approved
    """
    result = await service.start(plan_id)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


@router.post("/plans/{plan_id}/abandon", response_model=PlanResponse)
async def abandon_plan(
    plan_id: str,
    reason: str | None = None,
    service: PlanService = Depends(get_plan_service),
):
    """Abandon a plan.

    Args:
        plan_id: Plan identifier
        reason: Optional reason for abandoning
        service: Plan service instance

    Returns:
        Updated plan

    Raises:
        404: Plan not found
    """
    result = await service.abandon(plan_id, reason)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


# =========================================================================
# Step Operations
# =========================================================================


@router.post("/plans/{plan_id}/steps/{step_id}/complete", response_model=PlanResponse)
async def complete_step(
    plan_id: str,
    step_id: str,
    notes: str | None = None,
    service: PlanService = Depends(get_plan_service),
):
    """Mark a step as completed.

    Args:
        plan_id: Plan identifier
        step_id: Step identifier
        notes: Optional completion notes
        service: Plan service instance

    Returns:
        Updated plan

    Raises:
        404: Plan or step not found
        422: Step is already completed/skipped
    """
    result = await service.complete_step(plan_id, step_id, notes)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


@router.post("/plans/{plan_id}/steps/{step_id}/skip", response_model=PlanResponse)
async def skip_step(
    plan_id: str,
    step_id: str,
    reason: str | None = None,
    service: PlanService = Depends(get_plan_service),
):
    """Skip a step.

    Args:
        plan_id: Plan identifier
        step_id: Step identifier
        reason: Optional reason for skipping
        service: Plan service instance

    Returns:
        Updated plan

    Raises:
        404: Plan or step not found
        422: Step is already completed/skipped
    """
    result = await service.skip_step(plan_id, step_id, reason)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error


@router.post("/plans/{plan_id}/steps", response_model=PlanResponse)
async def add_step(
    plan_id: str,
    step: PlanStepInput,
    after_step_id: str | None = None,
    service: PlanService = Depends(get_plan_service),
):
    """Add a step to a plan.

    Args:
        plan_id: Plan identifier
        step: Step to add
        after_step_id: Insert after this step (or at end if None)
        service: Plan service instance

    Returns:
        Updated plan

    Raises:
        404: Plan not found
    """
    result = await service.add_step(plan_id, step, after_step_id)

    match result:
        case Ok(plan):
            return plan
        case Err(error):
            raise error
