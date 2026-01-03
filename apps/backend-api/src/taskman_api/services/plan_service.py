"""Plan service with plan management and step tracking.

Handles plan operations for plan-driven development workflows.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from taskman_api.core.errors import AppError, ConflictError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.plan import Plan
from taskman_api.repositories.plan_repository import PlanRepository
from taskman_api.schemas.plan import (
    PlanCreateRequest,
    PlanResponse,
    PlanStepInput,
    PlanUpdateRequest,
)

from .base import BaseService


def generate_plan_id() -> str:
    """Generate a unique plan ID with PLAN- prefix."""
    return f"PLAN-{uuid4().hex[:12].upper()}"


def generate_step_id() -> str:
    """Generate a unique step ID."""
    return f"STEP-{uuid4().hex[:8].upper()}"


class PlanService(
    BaseService[Plan, PlanCreateRequest, PlanUpdateRequest, PlanResponse]
):
    """Plan business logic and operations.

    Provides plan management including:
    - Plan lifecycle (draft, approve, execute, complete)
    - Step management with ordering and status tracking
    - Progress calculation and metrics

    Example:
        service = PlanService(session)
        result = await service.create(PlanCreateRequest(...))
        match result:
            case Ok(plan):
                print(f"Created plan: {plan.id}")
            case Err(error):
                print(f"Failed: {error.message}")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize PlanService.

        Args:
            session: Async database session
        """
        repository = PlanRepository(session)
        super().__init__(repository, Plan, PlanResponse)
        self.plan_repo = repository
        self.db_session = session

    async def create(
        self,
        request: PlanCreateRequest,
    ) -> Result[PlanResponse, AppError]:
        """Create new plan.

        Generates ID and step IDs if not provided.

        Args:
            request: Plan creation request

        Returns:
            Result containing created plan or error
        """
        plan_id = request.id or generate_plan_id()

        # Process steps to ensure they have IDs and order
        steps = []
        for i, step in enumerate(request.steps or []):
            step_data = step.model_dump()
            if not step_data.get("id"):
                step_data["id"] = generate_step_id()
            step_data["order"] = step_data.get("order", i + 1)
            step_data["status"] = step_data.get("status", "pending")
            steps.append(step_data)

        # Create model
        model_data = request.model_dump()
        model_data["id"] = plan_id
        model_data["steps"] = steps
        # Map metadata -> extra_metadata (SQLAlchemy reserves 'metadata')
        if "metadata" in model_data:
            model_data["extra_metadata"] = model_data.pop("metadata")
        entity = Plan(**model_data)

        try:
            created = await self.repository.create(entity)
            response = PlanResponse.model_validate(created)
            return Ok(response)
        except IntegrityError as e:
            return Err(
                ConflictError(
                    message=f"A Plan with ID '{plan_id}' already exists",
                    entity_type="Plan",
                    entity_id=plan_id,
                    original_error=str(e.orig) if e.orig else str(e),
                )
            )
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def approve(
        self,
        plan_id: str,
    ) -> Result[PlanResponse, NotFoundError | ValidationError | AppError]:
        """Approve a draft plan for execution.

        Args:
            plan_id: Plan identifier

        Returns:
            Result containing updated plan or error
        """
        find_result = await self.repository.find_by_id(plan_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                if entity.status != "draft":
                    return Err(
                        ValidationError(
                            message=f"Can only approve draft plans (current: {entity.status})",
                            field="status",
                            value=entity.status,
                        )
                    )

                entity.status = "approved"
                entity.approved_at = datetime.now(UTC)

                updated = await self.repository.update(entity)
                response = PlanResponse.model_validate(updated)
                return Ok(response)

    async def start(
        self,
        plan_id: str,
    ) -> Result[PlanResponse, NotFoundError | ValidationError | AppError]:
        """Start executing an approved plan.

        Args:
            plan_id: Plan identifier

        Returns:
            Result containing updated plan or error
        """
        find_result = await self.repository.find_by_id(plan_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                if entity.status not in ("approved", "in_progress"):
                    return Err(
                        ValidationError(
                            message=f"Can only start approved plans (current: {entity.status})",
                            field="status",
                            value=entity.status,
                        )
                    )

                entity.status = "in_progress"

                # Start first pending step
                steps = entity.steps or []
                for step in sorted(steps, key=lambda s: s.get("order", 0)):
                    if step.get("status") == "pending":
                        step["status"] = "in_progress"
                        step["started_at"] = datetime.now(UTC).isoformat()
                        break

                entity.steps = steps
                flag_modified(entity, "steps")

                updated = await self.repository.update(entity)
                response = PlanResponse.model_validate(updated)
                return Ok(response)

    async def complete_step(
        self,
        plan_id: str,
        step_id: str,
        notes: str | None = None,
    ) -> Result[PlanResponse, NotFoundError | ValidationError | AppError]:
        """Mark a step as completed.

        Args:
            plan_id: Plan identifier
            step_id: Step identifier
            notes: Optional completion notes

        Returns:
            Result containing updated plan or error
        """
        find_result = await self.repository.find_by_id(plan_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                steps = entity.steps or []
                step_found = False

                for step in steps:
                    if step.get("id") == step_id:
                        step_found = True
                        if step.get("status") not in ("pending", "in_progress"):
                            return Err(
                                ValidationError(
                                    message=f"Step is already {step.get('status')}",
                                    field="step_id",
                                    value=step_id,
                                )
                            )

                        step["status"] = "completed"
                        step["completed_at"] = datetime.now(UTC).isoformat()
                        if notes:
                            step["notes"] = notes
                        break

                if not step_found:
                    return Err(
                        NotFoundError(
                            message=f"Step {step_id} not found in plan",
                            entity_type="PlanStep",
                            entity_id=step_id,
                        )
                    )

                # Start next pending step
                for step in sorted(steps, key=lambda s: s.get("order", 0)):
                    if step.get("status") == "pending":
                        step["status"] = "in_progress"
                        step["started_at"] = datetime.now(UTC).isoformat()
                        break

                entity.steps = steps
                flag_modified(entity, "steps")

                # Check if all steps completed
                all_completed = all(
                    s.get("status") in ("completed", "skipped") for s in steps
                )
                if all_completed and steps:
                    entity.status = "completed"
                    entity.completed_at = datetime.now(UTC)

                updated = await self.repository.update(entity)
                response = PlanResponse.model_validate(updated)
                return Ok(response)

    async def skip_step(
        self,
        plan_id: str,
        step_id: str,
        reason: str | None = None,
    ) -> Result[PlanResponse, NotFoundError | ValidationError | AppError]:
        """Skip a step.

        Args:
            plan_id: Plan identifier
            step_id: Step identifier
            reason: Optional reason for skipping

        Returns:
            Result containing updated plan or error
        """
        find_result = await self.repository.find_by_id(plan_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                steps = entity.steps or []
                step_found = False

                for step in steps:
                    if step.get("id") == step_id:
                        step_found = True
                        if step.get("status") in ("completed", "skipped"):
                            return Err(
                                ValidationError(
                                    message=f"Step is already {step.get('status')}",
                                    field="step_id",
                                    value=step_id,
                                )
                            )

                        step["status"] = "skipped"
                        step["skipped_at"] = datetime.now(UTC).isoformat()
                        if reason:
                            step["skip_reason"] = reason
                        break

                if not step_found:
                    return Err(
                        NotFoundError(
                            message=f"Step {step_id} not found in plan",
                            entity_type="PlanStep",
                            entity_id=step_id,
                        )
                    )

                entity.steps = steps
                flag_modified(entity, "steps")

                # Start next pending step if current was in_progress
                for step in sorted(steps, key=lambda s: s.get("order", 0)):
                    if step.get("status") == "pending":
                        step["status"] = "in_progress"
                        step["started_at"] = datetime.now(UTC).isoformat()
                        break

                # Check if all steps done
                all_done = all(
                    s.get("status") in ("completed", "skipped") for s in steps
                )
                if all_done and steps:
                    entity.status = "completed"
                    entity.completed_at = datetime.now(UTC)

                updated = await self.repository.update(entity)
                response = PlanResponse.model_validate(updated)
                return Ok(response)

    async def add_step(
        self,
        plan_id: str,
        step: PlanStepInput,
        after_step_id: str | None = None,
    ) -> Result[PlanResponse, NotFoundError | AppError]:
        """Add a step to a plan.

        Args:
            plan_id: Plan identifier
            step: Step to add
            after_step_id: Insert after this step (or at end if None)

        Returns:
            Result containing updated plan or error
        """
        find_result = await self.repository.find_by_id(plan_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                steps = entity.steps or []

                # Create step data
                step_data = step.model_dump()
                step_data["id"] = step_data.get("id") or generate_step_id()
                step_data["status"] = step_data.get("status", "pending")

                # Determine order
                if after_step_id:
                    # Find position to insert
                    insert_idx = len(steps)
                    for i, s in enumerate(steps):
                        if s.get("id") == after_step_id:
                            insert_idx = i + 1
                            break

                    # Insert and reorder
                    steps.insert(insert_idx, step_data)
                    for i, s in enumerate(steps):
                        s["order"] = i + 1
                else:
                    # Add at end
                    step_data["order"] = len(steps) + 1
                    steps.append(step_data)

                entity.steps = steps
                flag_modified(entity, "steps")

                updated = await self.repository.update(entity)
                response = PlanResponse.model_validate(updated)
                return Ok(response)

    async def abandon(
        self,
        plan_id: str,
        reason: str | None = None,
    ) -> Result[PlanResponse, NotFoundError | AppError]:
        """Abandon a plan.

        Args:
            plan_id: Plan identifier
            reason: Optional reason for abandoning

        Returns:
            Result containing updated plan or error
        """
        find_result = await self.repository.find_by_id(plan_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                entity.status = "abandoned"
                if reason:
                    metadata = entity.extra_metadata or {}
                    metadata["abandon_reason"] = reason
                    entity.extra_metadata = metadata
                    flag_modified(entity, "extra_metadata")

                updated = await self.repository.update(entity)
                response = PlanResponse.model_validate(updated)
                return Ok(response)

    async def search(
        self,
        status: str | None = None,
        project_id: str | None = None,
        sprint_id: str | None = None,
        conversation_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[PlanResponse], AppError]:
        """Search plans with filters.

        Args:
            status: Optional status filter
            project_id: Optional project filter
            sprint_id: Optional sprint filter
            conversation_id: Optional conversation filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing filtered plans or error
        """
        if status:
            result = await self.plan_repo.find_by_status(status, limit, offset)
        elif project_id:
            result = await self.plan_repo.find_by_project(
                project_id, status, limit, offset
            )
        elif sprint_id:
            result = await self.plan_repo.find_by_sprint(
                sprint_id, status, limit, offset
            )
        elif conversation_id:
            result = await self.plan_repo.find_by_conversation(
                conversation_id, limit, offset
            )
        else:
            result = await self.repository.find_all(limit=limit, offset=offset)

        match result:
            case Ok(plans):
                responses = [PlanResponse.model_validate(p) for p in plans]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_drafts(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[PlanResponse], AppError]:
        """Get all draft plans.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing draft plans or error
        """
        result = await self.plan_repo.find_drafts(limit, offset)

        match result:
            case Ok(plans):
                responses = [PlanResponse.model_validate(p) for p in plans]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_in_progress(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[PlanResponse], AppError]:
        """Get all in-progress plans.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing in-progress plans or error
        """
        result = await self.plan_repo.find_in_progress(limit, offset)

        match result:
            case Ok(plans):
                responses = [PlanResponse.model_validate(p) for p in plans]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_stalled(
        self,
        days_inactive: int = 3,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[PlanResponse], AppError]:
        """Get stalled plans (in_progress but not updated recently).

        Args:
            days_inactive: Days without update to consider stalled
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing stalled plans or error
        """
        result = await self.plan_repo.find_stalled(days_inactive, limit, offset)

        match result:
            case Ok(plans):
                responses = [PlanResponse.model_validate(p) for p in plans]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_stats(self) -> Result[dict, AppError]:
        """Get plan statistics.

        Returns:
            Result containing stats dict or error
        """
        count_result = await self.plan_repo.count_by_status()

        match count_result:
            case Err(error):
                return Err(error)
            case Ok(counts):
                total = sum(counts.values())
                return Ok(
                    {
                        "total": total,
                        "by_status": counts,
                    }
                )
