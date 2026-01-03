"""
ActionList Repository

Repository pattern implementation for ActionList persistence with Result monad pattern.
Provides concrete implementation aligned with TaskMan-v2 SQLAlchemy backend.
Follows TaskRepository pattern with async/await and dependency injection.
"""

import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cf_core.models.action_list import ActionList
from cf_core.shared.result import Result

logger = logging.getLogger(__name__)


class ActionListRepository:
    """
    SQLAlchemy implementation of ActionList repository.

    Bridges cf_core domain models with TaskMan-v2 SQLAlchemy persistence layer.
    Uses Result monad pattern for explicit error handling.
    Supports dependency injection via FastAPI.

    Performance targets:
    - get_by_id: <5ms (indexed on primary key)
    - find_by_task_id: <50ms (GIN index on task_ids array)
    - find_by_project_id: <50ms (B-tree index on FK)
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with async database session.

        Args:
            session: SQLAlchemy async session (injected via FastAPI dependency)
        """
        self.session = session

    async def create(self, action_list: ActionList) -> Result[ActionList]:
        """
        Create new action list in database.

        Args:
            action_list: ActionList domain model to persist

        Returns:
            Result[ActionList]: Success with created entity, or Failure with error message

        Performance: <5ms for single insert (indexed on id)
        """
        try:
            # Import here to avoid circular dependency
            from taskman_api.models.action_list import ActionList as ActionListModel

            # Transform domain model to ORM model
            db_model = ActionListModel(
                id=action_list.id,
                name=action_list.name,
                description=action_list.description,
                status=action_list.status,
                owner=action_list.owner,
                tags=action_list.tags,
                project_id=action_list.project_id,
                sprint_id=action_list.sprint_id,
                task_ids=action_list.task_ids,
                items=action_list.items,
                geometry_shape=action_list.geometry_shape,
                priority=action_list.priority,
                due_date=action_list.due_date,
                evidence_refs=action_list.evidence_refs,
                extra_metadata=action_list.extra_metadata,
                notes=action_list.notes,
                parent_deleted_at=action_list.parent_deleted_at,
                parent_deletion_note=action_list.parent_deletion_note,
                created_at=action_list.created_at,
                updated_at=action_list.updated_at,
                completed_at=action_list.completed_at,
            )

            self.session.add(db_model)
            await self.session.commit()
            await self.session.refresh(db_model)

            logger.info(
                "action_list_created",
                extra={"list_id": action_list.id, "list_name": action_list.name},
            )

            return Result.success(self._model_to_domain(db_model))

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = f"Integrity constraint violation: {str(e.orig)}"
            logger.error("action_list_create_failed", extra={"error": error_msg})
            return Result.failure(error_msg)

        except SQLAlchemyError as e:
            await self.session.rollback()
            error_msg = f"Database error during create: {str(e)}"
            logger.error("action_list_create_error", extra={"error": error_msg})
            return Result.failure(error_msg)

    async def get_by_id(self, list_id: str) -> Result[ActionList | None]:
        """
        Retrieve action list by ID.

        Args:
            list_id: Action list identifier (AL-XXXX format)

        Returns:
            Result[ActionList | None]: Success with entity (or None if not found), or Failure

        Performance: <5ms (uses primary key index ix_action_lists_pkey)
        """
        try:
            from taskman_api.models.action_list import ActionList as ActionListModel

            stmt = select(ActionListModel).where(ActionListModel.id == list_id)
            result = await self.session.execute(stmt)
            db_model = result.scalar_one_or_none()

            if db_model is None:
                logger.debug("action_list_not_found", extra={"list_id": list_id})
                return Result.success(None)

            return Result.success(self._model_to_domain(db_model))

        except SQLAlchemyError as e:
            error_msg = f"Database error retrieving {list_id}: {str(e)}"
            logger.error("action_list_get_error", extra={"list_id": list_id, "error": str(e)})
            return Result.failure(error_msg)

    async def update(self, action_list: ActionList) -> Result[ActionList]:
        """
        Update existing action list.

        Args:
            action_list: Updated ActionList domain model

        Returns:
            Result[ActionList]: Success with updated entity, or Failure

        Note: Updates all fields except created_at (immutable)
        """
        try:
            from taskman_api.models.action_list import ActionList as ActionListModel

            # Fetch existing record
            stmt = select(ActionListModel).where(ActionListModel.id == action_list.id)
            result = await self.session.execute(stmt)
            db_model = result.scalar_one_or_none()

            if db_model is None:
                error_msg = f"ActionList '{action_list.id}' not found for update"
                logger.warning("action_list_update_not_found", extra={"list_id": action_list.id})
                return Result.failure(error_msg)

            # Update fields (excluding created_at which is immutable)
            db_model.name = action_list.name
            db_model.description = action_list.description
            db_model.status = action_list.status
            db_model.owner = action_list.owner
            db_model.tags = action_list.tags
            db_model.project_id = action_list.project_id
            db_model.sprint_id = action_list.sprint_id
            db_model.task_ids = action_list.task_ids
            db_model.items = action_list.items
            db_model.geometry_shape = action_list.geometry_shape
            db_model.priority = action_list.priority
            db_model.due_date = action_list.due_date
            db_model.evidence_refs = action_list.evidence_refs
            db_model.extra_metadata = action_list.extra_metadata
            db_model.notes = action_list.notes
            db_model.parent_deleted_at = action_list.parent_deleted_at
            db_model.parent_deletion_note = action_list.parent_deletion_note
            db_model.updated_at = action_list.updated_at
            db_model.completed_at = action_list.completed_at

            await self.session.commit()
            await self.session.refresh(db_model)

            logger.info("action_list_updated", extra={"list_id": action_list.id})

            return Result.success(self._model_to_domain(db_model))

        except IntegrityError as e:
            await self.session.rollback()
            error_msg = f"Integrity constraint violation during update: {str(e.orig)}"
            logger.error("action_list_update_integrity_error", extra={"error": error_msg})
            return Result.failure(error_msg)

        except SQLAlchemyError as e:
            await self.session.rollback()
            error_msg = f"Database error during update: {str(e)}"
            logger.error("action_list_update_error", extra={"error": error_msg})
            return Result.failure(error_msg)

    async def delete(self, list_id: str) -> Result[bool]:
        """
        Delete action list by ID (hard delete).

        Args:
            list_id: Action list identifier

        Returns:
            Result[bool]: True if deleted, False if not found, Failure on error

        Note: Consider implementing soft delete via parent_deleted_at field
        """
        try:
            from taskman_api.models.action_list import ActionList as ActionListModel

            stmt = select(ActionListModel).where(ActionListModel.id == list_id)
            result = await self.session.execute(stmt)
            db_model = result.scalar_one_or_none()

            if db_model is None:
                logger.debug("action_list_delete_not_found", extra={"list_id": list_id})
                return Result.success(False)

            await self.session.delete(db_model)
            await self.session.commit()

            logger.info("action_list_deleted", extra={"list_id": list_id})
            return Result.success(True)

        except SQLAlchemyError as e:
            await self.session.rollback()
            error_msg = f"Database error during delete: {str(e)}"
            logger.error("action_list_delete_error", extra={"list_id": list_id, "error": str(e)})
            return Result.failure(error_msg)

    async def find_by_task_id(self, task_id: str) -> Result[list[ActionList]]:
        """
        Find all action lists containing a specific task ID.

        Args:
            task_id: Task identifier to search for

        Returns:
            Result[List[ActionList]]: Success with matching lists, or Failure

        Performance: <50ms (uses GIN index ix_action_lists_task_ids for containment)
        Query: PostgreSQL uses @> operator; SQLite uses JSON containment
        """
        try:
            from taskman_api.models.action_list import ActionList as ActionListModel

            # PostgreSQL: Use array containment operator @>
            # SQLite: JSON_CONTAINS fallback (handled by StringList type adapter)
            stmt = select(ActionListModel).where(ActionListModel.task_ids.contains([task_id]))

            result = await self.session.execute(stmt)
            db_models = result.scalars().all()

            domain_models = [self._model_to_domain(model) for model in db_models]

            logger.debug(
                "action_list_find_by_task",
                extra={"task_id": task_id, "count": len(domain_models)},
            )

            return Result.success(domain_models)

        except SQLAlchemyError as e:
            error_msg = f"Database error finding lists by task_id {task_id}: {str(e)}"
            logger.error(
                "action_list_find_by_task_error", extra={"task_id": task_id, "error": str(e)}
            )
            return Result.failure(error_msg)

    async def find_by_project_id(self, project_id: str) -> Result[list[ActionList]]:
        """
        Find all action lists associated with a project.

        Args:
            project_id: Project identifier

        Returns:
            Result[List[ActionList]]: Success with matching lists, or Failure

        Performance: <50ms (uses B-tree index on project_id FK)
        """
        try:
            from taskman_api.models.action_list import ActionList as ActionListModel

            stmt = select(ActionListModel).where(ActionListModel.project_id == project_id)
            result = await self.session.execute(stmt)
            db_models = result.scalars().all()

            domain_models = [self._model_to_domain(model) for model in db_models]

            logger.debug(
                "action_list_find_by_project",
                extra={"project_id": project_id, "count": len(domain_models)},
            )

            return Result.success(domain_models)

        except SQLAlchemyError as e:
            error_msg = f"Database error finding lists by project_id {project_id}: {str(e)}"
            logger.error(
                "action_list_find_by_project_error",
                extra={"project_id": project_id, "error": str(e)},
            )
            return Result.failure(error_msg)

    async def list_all(self, skip: int = 0, limit: int = 100) -> Result[list[ActionList]]:
        """
        List all action lists with pagination.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return (max 1000)

        Returns:
            Result[List[ActionList]]: Success with paginated lists, or Failure

        Performance: <100ms for 100 records (uses ix_action_lists_created_at for ordering)
        """
        try:
            from taskman_api.models.action_list import ActionList as ActionListModel

            # Enforce limit bounds
            limit = min(limit, 1000)

            stmt = (
                select(ActionListModel)
                .order_by(ActionListModel.created_at.desc())
                .offset(skip)
                .limit(limit)
            )

            result = await self.session.execute(stmt)
            db_models = result.scalars().all()

            domain_models = [self._model_to_domain(model) for model in db_models]

            logger.debug(
                "action_list_list_all",
                extra={"skip": skip, "limit": limit, "count": len(domain_models)},
            )

            return Result.success(domain_models)

        except SQLAlchemyError as e:
            error_msg = f"Database error listing action lists: {str(e)}"
            logger.error("action_list_list_error", extra={"error": str(e)})
            return Result.failure(error_msg)

    # --- Private Helper Methods ---

    def _model_to_domain(self, db_model) -> ActionList:
        """
        Convert SQLAlchemy ORM model to cf_core domain model.

        Args:
            db_model: SQLAlchemy ActionList instance

        Returns:
            ActionList: cf_core domain model
        """
        return ActionList(
            id=db_model.id,
            name=db_model.name,
            description=db_model.description or "",
            status=db_model.status,
            owner=db_model.owner or "system",
            tags=db_model.tags or [],
            project_id=db_model.project_id,
            sprint_id=db_model.sprint_id,
            task_ids=db_model.task_ids or [],
            items=db_model.items or [],
            geometry_shape=db_model.geometry_shape,
            priority=db_model.priority,
            due_date=db_model.due_date,
            evidence_refs=db_model.evidence_refs or [],
            extra_metadata=db_model.extra_metadata or {},
            notes=db_model.notes,
            parent_deleted_at=db_model.parent_deleted_at,
            parent_deletion_note=db_model.parent_deletion_note or {},
            created_at=db_model.created_at,
            updated_at=db_model.updated_at,
            completed_at=db_model.completed_at,
        )
