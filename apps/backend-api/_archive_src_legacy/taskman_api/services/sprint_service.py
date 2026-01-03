"""Sprint service with velocity and burndown calculations.

Handles sprint operations, metrics, and sprint lifecycle management.
"""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.enums import SprintStatus, TaskStatus
from taskman_api.core.errors import AppError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.models.sprint import Sprint
from taskman_api.db.repositories.sprint_repository import SprintRepository
from taskman_api.db.repositories.task_repository import TaskRepository
from taskman_api.schemas.sprint import (
    SprintCreateRequest,
    SprintResponse,
    SprintUpdateRequest,
)

from .base import BaseService


class SprintService(
    BaseService[Sprint, SprintCreateRequest, SprintUpdateRequest, SprintResponse]
):
    """Sprint business logic and operations.

    Provides sprint management functionality including:
    - CRUD operations (inherited from BaseService)
    - Velocity calculation
    - Burndown chart data
    - Sprint lifecycle management

    Example:
        service = SprintService(session)
        velocity = await service.calculate_velocity("S-2025-01")
        match velocity:
            case Ok(points):
                print(f"Sprint velocity: {points} points")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize SprintService with session.

        Args:
            session: Async database session
        """
        repository = SprintRepository(session)
        super().__init__(repository, Sprint, SprintResponse)
        self.sprint_repo = repository
        self.task_repo = TaskRepository(session)
        self.session = session

    async def calculate_velocity(
        self,
        sprint_id: str,
    ) -> Result[float, NotFoundError | AppError]:
        """Calculate actual velocity from completed tasks.

        Sums estimate_points for all tasks with status=DONE in the sprint.

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result containing velocity (points) or error

        Example:
            result = await service.calculate_velocity("S-2025-01")
            match result:
                case Ok(velocity):
                    print(f"Completed {velocity} story points")
        """
        # Verify sprint exists
        sprint_result = await self.get(sprint_id)
        match sprint_result:
            case Err(error):
                return Err(error)
            case Ok(_):
                pass

        # Get all completed tasks in sprint
        tasks_result = await self.task_repo.find_by_sprint(
            sprint_id, status=TaskStatus.DONE, limit=1000, offset=0
        )

        match tasks_result:
            case Err(error):
                return Err(error)
            case Ok(tasks):
                # Sum estimate_points for completed tasks
                total_points = sum(
                    task.estimate_points for task in tasks if task.estimate_points
                )
                return Ok(total_points)

    async def get_burndown(
        self,
        sprint_id: str,
    ) -> Result[dict, NotFoundError | AppError]:
        """Calculate burndown chart data.

        Returns:
            {
                "total_points": float,
                "remaining_points": float,
                "completed_points": float,
                "days_total": int,
                "days_remaining": int,
                "ideal_burndown_rate": float,
                "actual_burndown_rate": float,
            }

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result containing burndown data or error

        Example:
            result = await service.get_burndown("S-2025-01")
            match result:
                case Ok(data):
                    print(f"Remaining: {data['remaining_points']} points")
                    print(f"Days left: {data['days_remaining']}")
        """
        # Get sprint
        sprint_result = await self.get(sprint_id)
        match sprint_result:
            case Err(error):
                return Err(error)
            case Ok(sprint):
                pass

        # Get all tasks in sprint
        all_tasks_result = await self.task_repo.find_by_sprint(
            sprint_id, status=None, limit=1000, offset=0
        )

        match all_tasks_result:
            case Err(error):
                return Err(error)
            case Ok(all_tasks):
                # Calculate points
                total_points = sum(
                    task.estimate_points for task in all_tasks if task.estimate_points
                )

                # Get completed tasks
                completed_tasks_result = await self.task_repo.find_by_sprint(
                    sprint_id, status=TaskStatus.DONE, limit=1000, offset=0
                )

                match completed_tasks_result:
                    case Err(error):
                        return Err(error)
                    case Ok(completed_tasks):
                        completed_points = sum(
                            task.estimate_points
                            for task in completed_tasks
                            if task.estimate_points
                        )
                        remaining_points = total_points - completed_points

                        # Calculate days
                        today = date.today()
                        days_total = (sprint.end_date - sprint.start_date).days
                        days_elapsed = max(0, (today - sprint.start_date).days)
                        days_remaining = max(0, (sprint.end_date - today).days)

                        # Calculate burndown rates
                        ideal_burndown_rate = (
                            total_points / days_total if days_total > 0 else 0.0
                        )
                        actual_burndown_rate = (
                            completed_points / days_elapsed if days_elapsed > 0 else 0.0
                        )

                        burndown_data = {
                            "total_points": total_points,
                            "remaining_points": remaining_points,
                            "completed_points": completed_points,
                            "days_total": days_total,
                            "days_elapsed": days_elapsed,
                            "days_remaining": days_remaining,
                            "ideal_burndown_rate": round(ideal_burndown_rate, 2),
                            "actual_burndown_rate": round(actual_burndown_rate, 2),
                            "on_track": actual_burndown_rate >= ideal_burndown_rate,
                        }

                        return Ok(burndown_data)

    async def change_status(
        self,
        sprint_id: str,
        new_status: SprintStatus,
    ) -> Result[SprintResponse, NotFoundError | AppError]:
        """Change sprint status.

        Args:
            sprint_id: Sprint identifier
            new_status: New sprint status

        Returns:
            Result containing updated sprint or error

        Example:
            result = await service.change_status("S-2025-01", SprintStatus.ACTIVE)
        """
        update_request = SprintUpdateRequest(status=new_status)
        return await self.update(sprint_id, update_request)

    async def get_current_sprints(
        self,
        current_date: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get currently active sprints.

        Args:
            current_date: Date to check (default: today)
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of current sprints or error

        Example:
            result = await service.get_current_sprints()
            match result:
                case Ok(sprints):
                    print(f"Found {len(sprints)} active sprints")
        """
        result = await self.sprint_repo.find_current_sprints(
            current_date, limit, offset
        )

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_by_project(
        self,
        project_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get sprints for project.

        Args:
            project_id: Project identifier
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of sprints or error

        Example:
            result = await service.get_by_project("P-TASKMAN")
        """
        result = await self.sprint_repo.find_by_project(project_id, limit, offset)

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_by_status(
        self,
        status: SprintStatus,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[SprintResponse], AppError]:
        """Get sprints by status.

        Args:
            status: Sprint status filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of sprints or error

        Example:
            result = await service.get_by_status(SprintStatus.ACTIVE)
        """
        result = await self.sprint_repo.find_by_status(status, limit, offset)

        match result:
            case Ok(sprints):
                responses = [
                    self.response_class.model_validate(sprint) for sprint in sprints
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def update_metrics(
        self,
        sprint_id: str,
    ) -> Result[SprintResponse, NotFoundError | AppError]:
        """Update sprint metrics fields.

        Recalculates and updates:
        - actual_points (from completed tasks)
        - Velocity metrics

        Args:
            sprint_id: Sprint identifier

        Returns:
            Result containing updated sprint or error

        Example:
            result = await service.update_metrics("S-2025-01")
        """
        # Calculate current velocity
        velocity_result = await self.calculate_velocity(sprint_id)

        match velocity_result:
            case Err(error):
                return Err(error)
            case Ok(actual_points):
                # Update sprint with calculated metrics
                update_request = SprintUpdateRequest(actual_points=actual_points)
                return await self.update(sprint_id, update_request)
