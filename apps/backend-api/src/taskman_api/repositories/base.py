"""
Base Repository.

Abstract base class for all repositories providing common CRUD operations.
"""

from abc import ABC
from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.db.base import Base

if TYPE_CHECKING:
    from taskman_api.core.errors import NotFoundError
    from taskman_api.core.result import Result

T = TypeVar("T", bound=Base)


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository with common CRUD operations.

    Subclasses must define:
    - model_class: The SQLAlchemy model class (either as class attribute or passed to __init__)
    """

    model_class: type[T]

    def __init__(
        self, model_or_session: type[T] | AsyncSession, session: AsyncSession | None = None
    ):
        """Initialize with async database session.

        Supports two patterns:
        1. BaseRepository(session) - model_class defined as class attribute
        2. BaseRepository(ModelClass, session) - model_class passed to constructor
        """
        if session is not None:
            # Pattern 2: model_class passed to constructor
            self.model_class = model_or_session  # type: ignore
            self.session = session
        else:
            # Pattern 1: session only, model_class is class attribute
            self.session = model_or_session  # type: ignore

    async def get_by_id(self, entity_id: str | UUID) -> T | None:
        """Get entity by ID."""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == entity_id)
        )
        return result.scalar_one_or_none()

    async def find_by_id(self, entity_id: str | UUID) -> "Result[T, NotFoundError]":
        """Find entity by ID, returning Result pattern.

        Args:
            entity_id: Entity identifier

        Returns:
            Ok(entity) if found, Err(NotFoundError) otherwise
        """
        from taskman_api.core.errors import NotFoundError
        from taskman_api.core.result import Err, Ok

        entity = await self.get_by_id(entity_id)
        if entity is None:
            return Err(
                NotFoundError(
                    resource_type=self.model_class.__name__,
                    resource_id=str(entity_id),
                )
            )
        return Ok(entity)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[T]:
        """Get all entities with pagination."""
        result = await self.session.execute(select(self.model_class).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Create a new entity."""
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """Update an existing entity."""
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: T) -> None:
        """Delete an entity."""
        await self.session.delete(entity)
        await self.session.commit()

    async def count(self) -> int:
        """Count total entities."""
        from sqlalchemy import func

        result = await self.session.execute(select(func.count()).select_from(self.model_class))
        return result.scalar() or 0

    async def exists(self, entity_id: str | UUID) -> bool:
        """Check if entity exists by ID.

        Provides default implementation using get_by_id.
        Subclasses may override for optimized queries.
        """
        entity = await self.get_by_id(entity_id)
        return entity is not None
