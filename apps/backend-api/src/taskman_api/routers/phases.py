"""Phase tracking API endpoints.

Provides REST endpoints for phase lifecycle management across
Tasks, Sprints, and Projects.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query

from taskman_api.core.enums import PhaseStatus
from taskman_api.core.result import Err, Ok
from taskman_api.dependencies import get_phase_service
from taskman_api.schemas.phase import (
    BlockedEntityResponse,
    BlockPhaseRequest,
    EntityInPhaseResponse,
    PhaseAnalyticsResponse,
    PhasesResponse,
    PhaseSummaryResponse,
    PhaseUpdateRequest,
    SkipPhaseRequest,
)
from taskman_api.services.phase_service import PhaseService

router = APIRouter()

# Entity type for path parameter
EntityType = Literal["task", "sprint", "project"]


# =============================================================================
# Phase CRUD Operations
# =============================================================================


@router.get(
    "/phases/{entity_type}/{entity_id}",
    response_model=PhasesResponse,
)
async def get_phases(
    entity_type: EntityType,
    entity_id: str,
    service: PhaseService = Depends(get_phase_service),
):
    """Get all phases for an entity.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        service: Phase service instance

    Returns:
        All phases with their current data

    Raises:
        404: Entity not found
    """
    result = await service.get_phases(entity_id, entity_type)

    match result:
        case Ok(phases):
            return PhasesResponse(
                entity_id=entity_id,
                entity_type=entity_type,
                phases=phases,
            )
        case Err(error):
            raise error


@router.get(
    "/phases/{entity_type}/{entity_id}/summary",
    response_model=PhaseSummaryResponse,
)
async def get_phase_summary(
    entity_type: EntityType,
    entity_id: str,
    service: PhaseService = Depends(get_phase_service),
):
    """Get phase summary with progress metrics.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        service: Phase service instance

    Returns:
        Phase summary including completion percentage and current phase

    Raises:
        404: Entity not found
    """
    result = await service.get_phase_summary(entity_id, entity_type)

    match result:
        case Ok(summary):
            return PhaseSummaryResponse(**summary)
        case Err(error):
            raise error


@router.patch(
    "/phases/{entity_type}/{entity_id}/{phase_name}",
    response_model=dict,
)
async def update_phase(
    entity_type: EntityType,
    entity_id: str,
    phase_name: str,
    request: PhaseUpdateRequest,
    service: PhaseService = Depends(get_phase_service),
):
    """Update a specific phase.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        phase_name: Name of the phase to update
        request: Update request with optional fields
        service: Phase service instance

    Returns:
        Updated phase data

    Raises:
        404: Entity not found
        422: Invalid phase name or status transition
    """
    # Build updates dict from request
    updates = {}

    if request.status is not None:
        updates["status"] = request.status.value

    if request.blocked_reason is not None:
        updates["blocked_reason"] = request.blocked_reason

    if request.skip_reason is not None:
        updates["skip_reason"] = request.skip_reason

    if request.additional_fields is not None:
        updates.update(request.additional_fields)

    result = await service.update_phase(entity_id, entity_type, phase_name, updates)

    match result:
        case Ok(phase_data):
            return phase_data
        case Err(error):
            raise error


# =============================================================================
# Phase Status Transitions
# =============================================================================


@router.post(
    "/phases/{entity_type}/{entity_id}/advance",
    response_model=PhasesResponse,
)
async def advance_phase(
    entity_type: EntityType,
    entity_id: str,
    service: PhaseService = Depends(get_phase_service),
):
    """Advance entity to the next phase.

    Completes the current in_progress phase and starts the next one.
    If no phase is in_progress, starts the first not_started phase.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        service: Phase service instance

    Returns:
        Updated phases

    Raises:
        404: Entity not found
        422: No phases available to advance
    """
    result = await service.advance_phase(entity_id, entity_type)

    match result:
        case Ok(phases):
            return PhasesResponse(
                entity_id=entity_id,
                entity_type=entity_type,
                phases=phases,
            )
        case Err(error):
            raise error


@router.post(
    "/phases/{entity_type}/{entity_id}/{phase_name}/block",
    response_model=dict,
)
async def block_phase(
    entity_type: EntityType,
    entity_id: str,
    phase_name: str,
    request: BlockPhaseRequest | None = None,
    service: PhaseService = Depends(get_phase_service),
):
    """Block a phase with optional reason.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        phase_name: Name of the phase to block
        request: Optional block reason
        service: Phase service instance

    Returns:
        Updated phase data

    Raises:
        404: Entity not found
        422: Invalid phase name or transition
    """
    blocked_reason = request.blocked_reason if request else None
    result = await service.block_phase(entity_id, entity_type, phase_name, blocked_reason)

    match result:
        case Ok(phase_data):
            return phase_data
        case Err(error):
            raise error


@router.post(
    "/phases/{entity_type}/{entity_id}/{phase_name}/unblock",
    response_model=dict,
)
async def unblock_phase(
    entity_type: EntityType,
    entity_id: str,
    phase_name: str,
    service: PhaseService = Depends(get_phase_service),
):
    """Unblock a phase and resume work.

    Sets the phase status back to in_progress.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        phase_name: Name of the phase to unblock
        service: Phase service instance

    Returns:
        Updated phase data

    Raises:
        404: Entity not found
        422: Invalid phase name or transition
    """
    result = await service.unblock_phase(entity_id, entity_type, phase_name)

    match result:
        case Ok(phase_data):
            return phase_data
        case Err(error):
            raise error


@router.post(
    "/phases/{entity_type}/{entity_id}/{phase_name}/skip",
    response_model=dict,
)
async def skip_phase(
    entity_type: EntityType,
    entity_id: str,
    phase_name: str,
    request: SkipPhaseRequest | None = None,
    service: PhaseService = Depends(get_phase_service),
):
    """Skip a phase with optional reason.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        phase_name: Name of the phase to skip
        request: Optional skip reason
        service: Phase service instance

    Returns:
        Updated phase data

    Raises:
        404: Entity not found
        422: Invalid phase name or transition
    """
    skip_reason = request.skip_reason if request else None
    result = await service.skip_phase(entity_id, entity_type, phase_name, skip_reason)

    match result:
        case Ok(phase_data):
            return phase_data
        case Err(error):
            raise error


@router.post(
    "/phases/{entity_type}/{entity_id}/{phase_name}/complete",
    response_model=dict,
)
async def complete_phase(
    entity_type: EntityType,
    entity_id: str,
    phase_name: str,
    service: PhaseService = Depends(get_phase_service),
):
    """Mark a phase as completed.

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        phase_name: Name of the phase to complete
        service: Phase service instance

    Returns:
        Updated phase data

    Raises:
        404: Entity not found
        422: Invalid phase name or transition
    """
    result = await service.set_phase_status(
        entity_id, entity_type, phase_name, PhaseStatus.COMPLETED
    )

    match result:
        case Ok(phase_data):
            return phase_data
        case Err(error):
            raise error


@router.post(
    "/phases/{entity_type}/{entity_id}/{phase_name}/start",
    response_model=dict,
)
async def start_phase(
    entity_type: EntityType,
    entity_id: str,
    phase_name: str,
    service: PhaseService = Depends(get_phase_service),
):
    """Start a phase (set to in_progress).

    Args:
        entity_type: Type of entity (task, sprint, project)
        entity_id: Entity identifier
        phase_name: Name of the phase to start
        service: Phase service instance

    Returns:
        Updated phase data

    Raises:
        404: Entity not found
        422: Invalid phase name or transition
    """
    result = await service.set_phase_status(
        entity_id, entity_type, phase_name, PhaseStatus.IN_PROGRESS
    )

    match result:
        case Ok(phase_data):
            return phase_data
        case Err(error):
            raise error


# =============================================================================
# Phase Analytics and Search
# =============================================================================


@router.get(
    "/phases/{entity_type}/search",
    response_model=list[EntityInPhaseResponse],
)
async def find_entities_in_phase(
    entity_type: EntityType,
    phase_name: str = Query(..., description="Phase name to filter by"),
    phase_status: PhaseStatus | None = Query(None, description="Optional status filter"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: PhaseService = Depends(get_phase_service),
):
    """Find entities in a specific phase.

    Args:
        entity_type: Type of entity to search (task, sprint, project)
        phase_name: Phase name to filter by
        phase_status: Optional status filter
        limit: Maximum results
        offset: Results to skip
        service: Phase service instance

    Returns:
        List of entities in the specified phase

    Raises:
        422: Invalid phase name
    """
    result = await service.find_entities_in_phase(
        entity_type, phase_name, phase_status, limit, offset
    )

    match result:
        case Ok(entities):
            return [EntityInPhaseResponse(**entity) for entity in entities]
        case Err(error):
            raise error


@router.get(
    "/phases/blocked",
    response_model=list[BlockedEntityResponse],
)
async def find_blocked_entities(
    entity_type: EntityType | None = Query(None, description="Optional entity type filter"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    service: PhaseService = Depends(get_phase_service),
):
    """Find all entities with blocked phases.

    Args:
        entity_type: Optional filter by entity type
        limit: Maximum results
        offset: Results to skip
        service: Phase service instance

    Returns:
        List of blocked entity summaries
    """
    result = await service.find_blocked_entities(entity_type, limit, offset)

    match result:
        case Ok(blocked):
            return [BlockedEntityResponse(**entity) for entity in blocked]
        case Err(error):
            raise error


@router.get(
    "/phases/{entity_type}/analytics",
    response_model=PhaseAnalyticsResponse,
)
async def get_phase_analytics(
    entity_type: EntityType,
    limit: int = Query(default=1000, ge=1, le=10000),
    offset: int = Query(default=0, ge=0),
    service: PhaseService = Depends(get_phase_service),
):
    """Get phase analytics for an entity type.

    Analyzes phase distribution and completion across entities.

    Args:
        entity_type: Type of entity to analyze
        limit: Maximum entities to analyze
        offset: Entities to skip
        service: Phase service instance

    Returns:
        Phase analytics with counts and percentages
    """
    # Get all entities and compute analytics
    repo = service._get_repository(entity_type)
    find_result = await repo.find_all(limit=limit, offset=offset)

    match find_result:
        case Err(error):
            raise error
        case Ok(entities):
            from taskman_api.services.phase_service import (
                PROJECT_PHASES,
                SPRINT_PHASES,
                TASK_PHASES,
            )

            # Get valid phases for this entity type
            phases_map = {
                "task": TASK_PHASES,
                "sprint": SPRINT_PHASES,
                "project": PROJECT_PHASES,
            }
            valid_phases = phases_map[entity_type]

            # Initialize counters
            by_phase: dict[str, dict[str, int]] = {}
            for phase in valid_phases:
                by_phase[phase] = {status.value: 0 for status in PhaseStatus}

            blocked_count = 0
            total_completion = 0.0

            for entity in entities:
                phases = entity.phases or {}
                entity_phases_completed = 0
                has_blocked = False

                for phase_name in valid_phases:
                    phase_data = phases.get(phase_name, {})
                    status = phase_data.get("status", "not_started")

                    # Count by status
                    if status in by_phase[phase_name]:
                        by_phase[phase_name][status] += 1

                    # Track completed/skipped
                    if status in ("completed", "skipped"):
                        entity_phases_completed += 1

                    # Track blocked
                    if status == "blocked":
                        has_blocked = True

                if has_blocked:
                    blocked_count += 1

                # Calculate completion percentage for this entity
                if valid_phases:
                    total_completion += (entity_phases_completed / len(valid_phases)) * 100

            total_entities = len(entities)
            average_completion_pct = total_completion / total_entities if total_entities > 0 else 0.0

            return PhaseAnalyticsResponse(
                entity_type=entity_type,
                total_entities=total_entities,
                by_phase=by_phase,
                blocked_count=blocked_count,
                average_completion_pct=round(average_completion_pct, 1),
            )
