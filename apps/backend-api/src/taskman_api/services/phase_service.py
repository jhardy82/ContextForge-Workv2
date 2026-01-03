"""Phase tracking service for entity lifecycle phases.

Provides business logic for phase management across Tasks, Sprints, and Projects.
Each entity type has different phases based on its purpose:
- Task: 4 phases (research, planning, implementation, testing)
- Sprint: 2 phases (planning, implementation)
- Project: 2 phases (research, planning)
"""

from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from taskman_api.core.enums import PhaseStatus
from taskman_api.core.errors import AppError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.repositories.project_repository import ProjectRepository
from taskman_api.repositories.sprint_repository import SprintRepository
from taskman_api.repositories.task_repository import TaskRepository

# Entity type literal
EntityType = Literal["task", "sprint", "project"]

# Phase names by entity type
TASK_PHASES = ["research", "planning", "implementation", "testing"]
SPRINT_PHASES = ["planning", "implementation"]
PROJECT_PHASES = ["research", "planning"]

# Default phase structures by entity type
TASK_PHASES_DEFAULT = {
    "research": {"status": "not_started", "has_research": False, "research_adequate": False},
    "planning": {"status": "not_started", "has_acceptance_criteria": False, "has_definition_of_done": False},
    "implementation": {"status": "not_started", "progress_pct": 0, "has_code_changes": False},
    "testing": {"status": "not_started", "has_unit_tests": False, "tests_passing": False},
}

SPRINT_PHASES_DEFAULT = {
    "planning": {"status": "not_started", "has_sprint_goal": False, "has_capacity_plan": False, "tasks_estimated": False},
    "implementation": {"status": "not_started", "progress_pct": 0, "tasks_completed": 0, "tasks_total": 0},
}

PROJECT_PHASES_DEFAULT = {
    "research": {"status": "not_started", "has_market_research": False, "has_technical_research": False, "research_adequate": False},
    "planning": {"status": "not_started", "has_prd": False, "has_architecture": False, "has_roadmap": False},
}


class PhaseService:
    """Phase tracking business logic for all entity types.

    Manages lifecycle phases for Tasks, Sprints, and Projects.
    Provides phase transition validation, status updates, and analytics.

    Example:
        service = PhaseService(session)
        result = await service.get_phases("T-001", "task")
        match result:
            case Ok(phases):
                print(f"Current phases: {phases}")
            case Err(error):
                print(f"Error: {error.message}")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PhaseService with database session.

        Args:
            session: Async database session
        """
        self.session = session
        self.task_repo = TaskRepository(session)
        self.sprint_repo = SprintRepository(session)
        self.project_repo = ProjectRepository(session)

    def _get_repository(self, entity_type: EntityType):
        """Get repository for entity type."""
        repos = {
            "task": self.task_repo,
            "sprint": self.sprint_repo,
            "project": self.project_repo,
        }
        return repos[entity_type]

    def _get_valid_phases(self, entity_type: EntityType) -> list[str]:
        """Get valid phase names for entity type."""
        phases = {
            "task": TASK_PHASES,
            "sprint": SPRINT_PHASES,
            "project": PROJECT_PHASES,
        }
        return phases[entity_type]

    async def get_phases(
        self,
        entity_id: str,
        entity_type: EntityType,
    ) -> Result[dict[str, Any], NotFoundError | AppError]:
        """Get all phases for an entity.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity (task, sprint, project)

        Returns:
            Result containing phases dict or error

        Example:
            result = await service.get_phases("T-001", "task")
            match result:
                case Ok(phases):
                    print(f"Research: {phases['research']['status']}")
        """
        repo = self._get_repository(entity_type)
        find_result = await repo.find_by_id(entity_id)

        match find_result:
            case Ok(entity):
                return Ok(entity.phases)
            case Err(error):
                return Err(error)

    async def get_phase_status(
        self,
        entity_id: str,
        entity_type: EntityType,
        phase_name: str,
    ) -> Result[PhaseStatus, NotFoundError | ValidationError | AppError]:
        """Get status of a specific phase.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            phase_name: Name of the phase (research, planning, etc.)

        Returns:
            Result containing PhaseStatus or error

        Example:
            result = await service.get_phase_status("T-001", "task", "research")
            match result:
                case Ok(status):
                    print(f"Research phase is {status.value}")
        """
        valid_phases = self._get_valid_phases(entity_type)
        if phase_name not in valid_phases:
            return Err(
                ValidationError(
                    message=f"Invalid phase '{phase_name}' for {entity_type}. Valid phases: {valid_phases}",
                    field="phase_name",
                    value=phase_name,
                )
            )

        phases_result = await self.get_phases(entity_id, entity_type)

        match phases_result:
            case Ok(phases):
                phase_data = phases.get(phase_name, {})
                status_str = phase_data.get("status", "not_started")
                return Ok(PhaseStatus(status_str))
            case Err(error):
                return Err(error)

    async def update_phase(
        self,
        entity_id: str,
        entity_type: EntityType,
        phase_name: str,
        updates: dict[str, Any],
    ) -> Result[dict[str, Any], NotFoundError | ValidationError | AppError]:
        """Update a specific phase with new data.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            phase_name: Name of the phase to update
            updates: Dict of fields to update in the phase

        Returns:
            Result containing updated phase data or error

        Example:
            result = await service.update_phase(
                "T-001", "task", "research",
                {"status": "in_progress", "has_research": True}
            )
        """
        valid_phases = self._get_valid_phases(entity_type)
        if phase_name not in valid_phases:
            return Err(
                ValidationError(
                    message=f"Invalid phase '{phase_name}' for {entity_type}. Valid phases: {valid_phases}",
                    field="phase_name",
                    value=phase_name,
                )
            )

        repo = self._get_repository(entity_type)
        find_result = await repo.find_by_id(entity_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                # Get current phases
                phases = dict(entity.phases)  # Make a copy

                # Update the specific phase
                if phase_name not in phases:
                    phases[phase_name] = {}

                phases[phase_name].update(updates)

                # Update entity - must reassign AND flag as modified
                # SQLAlchemy doesn't detect nested dict mutations automatically
                entity.phases = phases
                flag_modified(entity, "phases")
                update_result = await repo.update(entity)

                match update_result:
                    case Ok(updated_entity):
                        return Ok(updated_entity.phases[phase_name])
                    case Err(error):
                        return Err(error)

    async def set_phase_status(
        self,
        entity_id: str,
        entity_type: EntityType,
        phase_name: str,
        status: PhaseStatus,
    ) -> Result[dict[str, Any], NotFoundError | ValidationError | AppError]:
        """Set status for a specific phase.

        Validates phase transitions according to allowed rules.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            phase_name: Name of the phase
            status: New status for the phase

        Returns:
            Result containing updated phase data or error

        Example:
            result = await service.set_phase_status(
                "T-001", "task", "research", PhaseStatus.COMPLETED
            )
        """
        # Validate the status transition
        current_status_result = await self.get_phase_status(entity_id, entity_type, phase_name)

        match current_status_result:
            case Err(error):
                return Err(error)
            case Ok(current_status):
                if not self._is_valid_phase_transition(current_status, status):
                    return Err(
                        ValidationError(
                            message=f"Invalid phase transition: {current_status.value} -> {status.value}",
                            field="status",
                            value=status.value,
                        )
                    )

                return await self.update_phase(
                    entity_id, entity_type, phase_name,
                    {"status": status.value}
                )

    def _is_valid_phase_transition(
        self,
        current: PhaseStatus,
        new: PhaseStatus,
    ) -> bool:
        """Validate phase status transition.

        Transition Matrix:
        - NOT_STARTED -> IN_PROGRESS, SKIPPED
        - IN_PROGRESS -> COMPLETED, BLOCKED, SKIPPED
        - BLOCKED -> IN_PROGRESS, SKIPPED
        - COMPLETED -> (no transitions - terminal)
        - SKIPPED -> (no transitions - terminal)

        Args:
            current: Current phase status
            new: Requested new status

        Returns:
            True if transition is valid
        """
        valid_transitions: dict[PhaseStatus, list[PhaseStatus]] = {
            PhaseStatus.NOT_STARTED: [PhaseStatus.IN_PROGRESS, PhaseStatus.SKIPPED],
            PhaseStatus.IN_PROGRESS: [PhaseStatus.COMPLETED, PhaseStatus.BLOCKED, PhaseStatus.SKIPPED],
            PhaseStatus.BLOCKED: [PhaseStatus.IN_PROGRESS, PhaseStatus.SKIPPED],
            PhaseStatus.COMPLETED: [],  # Terminal state
            PhaseStatus.SKIPPED: [],  # Terminal state
        }

        return new in valid_transitions.get(current, [])

    async def advance_phase(
        self,
        entity_id: str,
        entity_type: EntityType,
    ) -> Result[dict[str, Any], NotFoundError | ValidationError | AppError]:
        """Advance entity to the next phase.

        Finds the first incomplete phase and marks it as in_progress,
        or if current phase is in_progress, marks it as completed
        and starts the next phase.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity

        Returns:
            Result containing updated phases or error

        Example:
            result = await service.advance_phase("T-001", "task")
            match result:
                case Ok(phases):
                    print(f"Advanced to next phase")
        """
        phases_result = await self.get_phases(entity_id, entity_type)

        match phases_result:
            case Err(error):
                return Err(error)
            case Ok(phases):
                valid_phases = self._get_valid_phases(entity_type)

                # Find current phase (first in_progress) or next phase to start
                current_phase = None
                next_phase = None

                for phase_name in valid_phases:
                    phase_data = phases.get(phase_name, {})
                    status = phase_data.get("status", "not_started")

                    if status == "in_progress":
                        current_phase = phase_name
                        # Find next phase
                        idx = valid_phases.index(phase_name)
                        if idx + 1 < len(valid_phases):
                            next_phase = valid_phases[idx + 1]
                        break
                    elif status == "not_started" and next_phase is None:
                        next_phase = phase_name

                if current_phase:
                    # Complete current phase
                    await self.set_phase_status(
                        entity_id, entity_type, current_phase, PhaseStatus.COMPLETED
                    )
                    # Start next phase if exists
                    if next_phase:
                        await self.set_phase_status(
                            entity_id, entity_type, next_phase, PhaseStatus.IN_PROGRESS
                        )
                elif next_phase:
                    # No current phase, start next phase
                    await self.set_phase_status(
                        entity_id, entity_type, next_phase, PhaseStatus.IN_PROGRESS
                    )
                else:
                    return Err(
                        ValidationError(
                            message="No phases available to advance",
                            field="phases",
                        )
                    )

                # Return updated phases
                return await self.get_phases(entity_id, entity_type)

    async def block_phase(
        self,
        entity_id: str,
        entity_type: EntityType,
        phase_name: str,
        blocked_reason: str | None = None,
    ) -> Result[dict[str, Any], NotFoundError | ValidationError | AppError]:
        """Block a phase with optional reason.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            phase_name: Name of the phase to block
            blocked_reason: Optional reason for blocking

        Returns:
            Result containing updated phase data or error

        Example:
            result = await service.block_phase(
                "T-001", "task", "implementation",
                "Waiting for design approval"
            )
        """
        updates: dict[str, Any] = {"status": PhaseStatus.BLOCKED.value}
        if blocked_reason:
            updates["blocked_reason"] = blocked_reason

        return await self.update_phase(entity_id, entity_type, phase_name, updates)

    async def unblock_phase(
        self,
        entity_id: str,
        entity_type: EntityType,
        phase_name: str,
    ) -> Result[dict[str, Any], NotFoundError | ValidationError | AppError]:
        """Unblock a phase and resume work.

        Sets the phase status back to in_progress and clears blocked_reason.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            phase_name: Name of the phase to unblock

        Returns:
            Result containing updated phase data or error

        Example:
            result = await service.unblock_phase("T-001", "task", "implementation")
        """
        updates = {
            "status": PhaseStatus.IN_PROGRESS.value,
            "blocked_reason": None,
        }

        return await self.update_phase(entity_id, entity_type, phase_name, updates)

    async def skip_phase(
        self,
        entity_id: str,
        entity_type: EntityType,
        phase_name: str,
        skip_reason: str | None = None,
    ) -> Result[dict[str, Any], NotFoundError | ValidationError | AppError]:
        """Skip a phase with optional reason.

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity
            phase_name: Name of the phase to skip
            skip_reason: Optional reason for skipping

        Returns:
            Result containing updated phase data or error

        Example:
            result = await service.skip_phase(
                "T-001", "task", "research",
                "Already researched in parent task"
            )
        """
        updates: dict[str, Any] = {"status": PhaseStatus.SKIPPED.value}
        if skip_reason:
            updates["skip_reason"] = skip_reason

        return await self.update_phase(entity_id, entity_type, phase_name, updates)

    async def get_phase_summary(
        self,
        entity_id: str,
        entity_type: EntityType,
    ) -> Result[dict[str, Any], NotFoundError | AppError]:
        """Get summary of all phases for an entity.

        Returns a summary including:
        - current_phase: Name of current active phase
        - phases_completed: Number of completed phases
        - phases_total: Total number of phases
        - completion_pct: Percentage of phases completed
        - phases: Full phase details

        Args:
            entity_id: Entity identifier
            entity_type: Type of entity

        Returns:
            Result containing summary dict or error

        Example:
            result = await service.get_phase_summary("T-001", "task")
            match result:
                case Ok(summary):
                    print(f"Progress: {summary['completion_pct']}%")
        """
        phases_result = await self.get_phases(entity_id, entity_type)

        match phases_result:
            case Err(error):
                return Err(error)
            case Ok(phases):
                valid_phases = self._get_valid_phases(entity_type)
                phases_completed = 0
                current_phase = None

                for phase_name in valid_phases:
                    phase_data = phases.get(phase_name, {})
                    status = phase_data.get("status", "not_started")

                    if status == "completed":
                        phases_completed += 1
                    elif status == "in_progress":
                        current_phase = phase_name
                    elif status == "skipped":
                        phases_completed += 1  # Count skipped as "done"

                phases_total = len(valid_phases)
                completion_pct = (phases_completed / phases_total * 100) if phases_total > 0 else 0

                return Ok({
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "current_phase": current_phase,
                    "phases_completed": phases_completed,
                    "phases_total": phases_total,
                    "completion_pct": round(completion_pct, 1),
                    "phases": phases,
                })

    async def find_entities_in_phase(
        self,
        entity_type: EntityType,
        phase_name: str,
        phase_status: PhaseStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[dict[str, Any]], ValidationError | AppError]:
        """Find entities in a specific phase with optional status filter.

        Args:
            entity_type: Type of entity to search
            phase_name: Name of the phase to filter by
            phase_status: Optional status filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of entity summaries or error

        Example:
            result = await service.find_entities_in_phase(
                "task", "implementation", PhaseStatus.BLOCKED
            )
        """
        valid_phases = self._get_valid_phases(entity_type)
        if phase_name not in valid_phases:
            return Err(
                ValidationError(
                    message=f"Invalid phase '{phase_name}' for {entity_type}",
                    field="phase_name",
                    value=phase_name,
                )
            )

        repo = self._get_repository(entity_type)
        find_result = await repo.find_all(limit=limit, offset=offset)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entities):
                results = []
                for entity in entities:
                    phases = entity.phases or {}
                    phase_data = phases.get(phase_name, {})
                    status = phase_data.get("status", "not_started")

                    # Filter by status if specified
                    if phase_status and status != phase_status.value:
                        continue

                    results.append({
                        "id": entity.id,
                        "phase": phase_name,
                        "status": status,
                        "phase_data": phase_data,
                    })

                return Ok(results)

    async def find_blocked_entities(
        self,
        entity_type: EntityType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[dict[str, Any]], AppError]:
        """Find all entities with blocked phases.

        Args:
            entity_type: Optional filter by entity type
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of blocked entity summaries

        Example:
            result = await service.find_blocked_entities("task")
            match result:
                case Ok(blocked):
                    print(f"Found {len(blocked)} blocked tasks")
        """
        results: list[dict[str, Any]] = []
        entity_types = [entity_type] if entity_type else ["task", "sprint", "project"]

        for etype in entity_types:
            repo = self._get_repository(etype)  # type: ignore
            find_result = await repo.find_all(limit=limit, offset=offset)

            match find_result:
                case Err(_):
                    continue  # Skip errors, collect what we can
                case Ok(entities):
                    for entity in entities:
                        phases = entity.phases or {}
                        for phase_name, phase_data in phases.items():
                            if phase_data.get("status") == "blocked":
                                results.append({
                                    "entity_type": etype,
                                    "entity_id": entity.id,
                                    "phase": phase_name,
                                    "blocked_reason": phase_data.get("blocked_reason"),
                                })

        return Ok(results)
