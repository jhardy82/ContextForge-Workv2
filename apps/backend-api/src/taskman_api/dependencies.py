"""
FastAPI Dependencies.

Provides dependency injection for database sessions, repositories, and authentication.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from cf_core.dao.context import ContextRepository
from cf_core.dao.qse import QSERepository
from cf_core.services.qse import QSEService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.auth import User, get_current_admin_user, get_current_user
from taskman_api.db.session import AsyncSessionLocal, manager
from taskman_api.repositories.action_list_repository import ActionListRepository
from taskman_api.repositories.postgres_project_repository import PostgresProjectRepository
from taskman_api.repositories.postgres_sprint_repository import PostgresSprintRepository
from taskman_api.repositories.postgres_task_repository import PostgresTaskRepository
from taskman_api.repositories.project_repository import ProjectRepository
from taskman_api.repositories.sprint_repository import SprintRepository
from taskman_api.repositories.task_repository import TaskRepository
from taskman_api.services.action_list_service import ActionListService
from taskman_api.services.checklist_service import ChecklistService
from taskman_api.services.conversation_service import ConversationSessionService
from taskman_api.services.phase_service import PhaseService
from taskman_api.services.plan_service import PlanService
from taskman_api.services.project_service import ProjectService
from taskman_api.services.sprint_service import SprintService
from taskman_api.services.task_service import TaskService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Type alias for cleaner dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db_session)]


# Repository dependencies
def get_task_repository(session: DBSession) -> TaskRepository:
    """Get TaskRepository instance with injected session."""
    if not manager._using_fallback:
        return PostgresTaskRepository(session)
    return TaskRepository(session)


def get_project_repository(session: DBSession) -> ProjectRepository:
    """Get ProjectRepository instance with injected session."""
    if not manager._using_fallback:
        return PostgresProjectRepository(session)
    return ProjectRepository(session)


def get_sprint_repository(session: DBSession) -> SprintRepository:
    """Get SprintRepository instance with injected session."""
    if not manager._using_fallback:
        return PostgresSprintRepository(session)
    return SprintRepository(session)


def get_action_list_repository(session: DBSession) -> ActionListRepository:
    """Get ActionListRepository instance with injected session."""
    return ActionListRepository(session)


def get_qse_repository(session: DBSession) -> "QSERepository":
    """Get QSERepository instance from cf_core with injected session."""
    if not CF_CORE_AVAILABLE:
        raise ImportError("cf_core module is not available")
    return QSERepository(session)


def get_context_repository(session: DBSession) -> "ContextRepository":
    """Get ContextRepository instance from cf_core with injected session."""
    if not CF_CORE_AVAILABLE:
        raise ImportError("cf_core module is not available")
    return ContextRepository(session)


# Service dependencies
def get_task_service(session: DBSession) -> TaskService:
    """Get TaskService instance with injected session."""
    return TaskService(session)


def get_project_service(session: DBSession) -> ProjectService:
    """Get ProjectService instance with injected session."""
    return ProjectService(session)


def get_sprint_service(session: DBSession) -> SprintService:
    """Get SprintService instance with injected session."""
    return SprintService(session)


def get_action_list_service(session: DBSession) -> ActionListService:
    """Get ActionListService instance with injected session."""
    return ActionListService(session)


def get_checklist_service(session: DBSession) -> ChecklistService:
    """Get ChecklistService instance with injected session."""
    return ChecklistService(session)


def get_conversation_service(session: DBSession) -> ConversationSessionService:
    """Get ConversationSessionService instance with injected session."""
    return ConversationSessionService(session)


def get_phase_service(session: DBSession) -> PhaseService:
    """Get PhaseService instance with injected session."""
    return PhaseService(session)


def get_plan_service(session: DBSession) -> PlanService:
    """Get PlanService instance with injected session."""
    return PlanService(session)


def get_qse_service(session: DBSession) -> "QSEService":
    """Get QSEService instance from cf_core with injected session."""
    if not CF_CORE_AVAILABLE:
        raise ImportError("cf_core module is not available")
    return QSEService(get_qse_repository(session))


# Type aliases for repository injection
TaskRepo = Annotated[TaskRepository, Depends(get_task_repository)]
ProjectRepo = Annotated[ProjectRepository, Depends(get_project_repository)]
SprintRepo = Annotated[SprintRepository, Depends(get_sprint_repository)]
ActionListRepo = Annotated[ActionListRepository, Depends(get_action_list_repository)]
ContextRepo = Annotated[ContextRepository, Depends(get_context_repository)]

# Type aliases for service injection
TaskSvc = Annotated[TaskService, Depends(get_task_service)]
ProjectSvc = Annotated[ProjectService, Depends(get_project_service)]
SprintSvc = Annotated[SprintService, Depends(get_sprint_service)]
ActionListSvc = Annotated[ActionListService, Depends(get_action_list_service)]
QSESvc = Annotated[QSEService, Depends(get_qse_service)]


# Export auth dependencies for router use
__all__ = [
    "get_current_user",
    "get_current_admin_user",
    "User",
    "DBSession",
    "TaskRepo",
    "ProjectRepo",
    "SprintRepo",
    "ActionListRepo",
    "ContextRepo",
    "TaskSvc",
    "ProjectSvc",
    "SprintSvc",
    "ActionListSvc",
    "QSEService",
]
