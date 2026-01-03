"""Base repository with generic CRUD operations.

Implements the Repository pattern with Result monad for type-safe error handling.
"""

from collections.abc import Sequence
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import (
    AppError,
    ConflictError,
    DatabaseError,
    NotFoundError,
    ValidationError,
)
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.base import Base


@runtime_checkable
class HasId(Protocol):
    """Protocol for entities with an id attribute."""

    id: Any


T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic repository for CRUD operations with Result monad.

    Args:
        model: SQLAlchemy model class
        session: Async database session

    Example:
        ```python
        async with get_db() as session:
            repo = BaseRepository(Task, session)
            result = await repo.find_by_id("T-001")
            match result:
                case Ok(task):
                    print(f"Found: {task.title}")
                case Err(error):
                    print(f"Error: {error.message}")
        ```
    """

    def __init__(self, model: type[T], session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def create(self, entity: T) -> Result[T, DatabaseError | ConflictError]:
        """Create a new entity.

        Args:
            entity: Entity instance to create

        Returns:
            Result with created entity or error

        Example:
            ```python
            task = Task(id="T-001", title="New Task", ...)
            result = await repo.create(task)
            ```
        """
        try:
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return Ok(entity)
        except IntegrityError as e:
            await self.session.rollback()
            return Err(
                ConflictError(
                    message=f"Entity with id {getattr(entity, 'id', None)} already exists",
                    entity_type=self.model.__name__,
                    entity_id=str(getattr(entity, "id", None)),
                    constraint=str(e.orig),
                )
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            return Err(
                DatabaseError(
                    message=f"Failed to create {self.model.__name__}",
                    operation="create",
                    details=str(e),
                )
            )

    async def find_by_id(self, entity_id: str) -> Result[T, NotFoundError | DatabaseError]:
        """Find entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result with found entity or error

        Example:
            ```python
            result = await repo.find_by_id("T-001")
            ```
        """
        try:
            # SQLAlchemy column access on model class is dynamic
            stmt = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
            result = await self.session.execute(stmt)
            entity = result.scalar_one_or_none()

            if entity is None:
                return Err(
                    NotFoundError(
                        message=f"{self.model.__name__} with id {entity_id} not found",
                        entity_type=self.model.__name__,
                        entity_id=entity_id,
                    )
                )

            return Ok(entity)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find {self.model.__name__}",
                    operation="find_by_id",
                    details=str(e),
                )
            )

    async def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[T], DatabaseError | ValidationError]:
        """Find all entities with pagination.

        Args:
            limit: Maximum number of results (default 100, max 1000)
            offset: Number of results to skip (default 0)

        Returns:
            Result with list of entities or error

        Example:
            ```python
            result = await repo.find_all(limit=50, offset=0)
            ```
        """
        try:
            # Validate pagination params
            if limit > 1000:
                return Err(
                    ValidationError(
                        message="Limit cannot exceed 1000",
                        field="limit",
                        value=limit,
                    )
                )
            if offset < 0:
                return Err(
                    ValidationError(
                        message="Offset cannot be negative",
                        field="offset",
                        value=offset,
                    )
                )

            stmt = select(self.model).limit(limit).offset(offset)
            result = await self.session.execute(stmt)
            entities = result.scalars().all()
            return Ok(entities)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find {self.model.__name__} entities",
                    operation="find_all",
                    details=str(e),
                )
            )

    async def update(self, entity: T) -> Result[T, NotFoundError | DatabaseError]:
        """Update an existing entity.

        Args:
            entity: Entity instance with updated values

        Returns:
            Result with updated entity or error

        Example:
            ```python
            task.title = "Updated Title"
            result = await repo.update(task)
            ```
        """
        try:
            entity_id: str = entity.id  # type: ignore[attr-defined]

            # Check if entity exists
            exists_result = await self.find_by_id(entity_id)
            if isinstance(exists_result, Err):
                return exists_result

            await self.session.merge(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return Ok(entity)
        except SQLAlchemyError as e:
            await self.session.rollback()
            return Err(
                DatabaseError(
                    message=f"Failed to update {self.model.__name__}",
                    operation="update",
                    details=str(e),
                )
            )

    async def delete(self, entity_id: str) -> Result[bool, NotFoundError | DatabaseError]:
        """Delete entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result with True if deleted, or error

        Example:
            ```python
            result = await repo.delete("T-001")
            ```
        """
        try:
            # Check if entity exists
            exists_result = await self.find_by_id(entity_id)
            if isinstance(exists_result, Err):
                return exists_result

            stmt = delete(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
            await self.session.execute(stmt)
            await self.session.flush()
            return Ok(True)
        except SQLAlchemyError as e:
            await self.session.rollback()
            return Err(
                DatabaseError(
                    message=f"Failed to delete {self.model.__name__}",
                    operation="delete",
                    details=str(e),
                )
            )

    async def exists(self, entity_id: str) -> Result[bool, DatabaseError]:
        """Check if entity exists by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result with True if exists, False otherwise

        Example:
            ```python
            result = await repo.exists("T-001")
            ```
        """
        try:
            # SQLAlchemy column access on model class is dynamic
            stmt = select(self.model.id).where(self.model.id == entity_id)  # type: ignore[attr-defined]
            result = await self.session.execute(stmt)
            exists = result.scalar_one_or_none() is not None
            return Ok(exists)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to check existence of {self.model.__name__}",
                    operation="exists",
                    details=str(e),
                )
            )

    async def count(self) -> Result[int, DatabaseError]:
        """Count total number of entities.

        Returns:
            Result with count or error

        Example:
            ```python
            result = await repo.count()
            ```
        """
        try:
            stmt = select(self.model)
            result = await self.session.execute(stmt)
            count = len(result.scalars().all())
            return Ok(count)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to count {self.model.__name__} entities",
                    operation="count",
                    details=str(e),
                )
            )
