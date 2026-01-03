"""FastAPI dependencies for dependency injection.

Provides database sessions and service instances to route handlers.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.db.session import get_session_factory
from taskman_api.services.action_list_service import ActionListService
from taskman_api.services.checklist_service import ChecklistService
from taskman_api.services.conversation_service import ConversationSessionService
from taskman_api.services.phase_service import PhaseService
from taskman_api.services.plan_service import PlanService
from taskman_api.services.project_service import ProjectService
from taskman_api.services.sprint_service import SprintService
from taskman_api.services.task_service import TaskService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session.

    Yields database session and ensures proper cleanup with commit.

    Yields:
        AsyncSession: Database session

    Example:
        @router.get("/tasks")
        async def list_tasks(db: AsyncSession = Depends(get_db)):
            # Use db session
            pass
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()  # Commit changes after successful request
        except Exception:
            await session.rollback()  # Rollback on error
            raise
        finally:
            await session.close()


async def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """Get TaskService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        TaskService: Task service instance

    Example:
        @router.post("/tasks")
        async def create_task(
            request: TaskCreateRequest,
            service: TaskService = Depends(get_task_service)
        ):
            result = await service.create(request)
            # Handle result
    """
    return TaskService(db)


async def get_project_service(
    db: AsyncSession = Depends(get_db),
) -> ProjectService:
    """Get ProjectService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        ProjectService: Project service instance
    """
    return ProjectService(db)


async def get_sprint_service(db: AsyncSession = Depends(get_db)) -> SprintService:
    """Get SprintService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        SprintService: Sprint service instance
    """
    return SprintService(db)


async def get_action_list_service(
    db: AsyncSession = Depends(get_db),
) -> ActionListService:
    """Get ActionListService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        ActionListService: ActionList service instance
    """
    return ActionListService(db)


async def get_phase_service(
    db: AsyncSession = Depends(get_db),
) -> PhaseService:
    """Get PhaseService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        PhaseService: Phase service instance
    """
    return PhaseService(db)


# =========================================================================
# State Store Service Dependencies
# =========================================================================


async def get_conversation_service(
    db: AsyncSession = Depends(get_db),
) -> ConversationSessionService:
    """Get ConversationSessionService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        ConversationSessionService: Conversation service instance
    """
    return ConversationSessionService(db)


async def get_plan_service(
    db: AsyncSession = Depends(get_db),
) -> PlanService:
    """Get PlanService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        PlanService: Plan service instance
    """
    return PlanService(db)


async def get_checklist_service(
    db: AsyncSession = Depends(get_db),
) -> ChecklistService:
    """Get ChecklistService instance.

    Args:
        db: Database session from get_db dependency

    Returns:
        ChecklistService: Checklist service instance
    """
    return ChecklistService(db)
