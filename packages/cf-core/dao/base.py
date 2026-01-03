from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Select

from cf_core.logging import ulog

T = TypeVar("T")


class Base(AsyncAttrs, DeclarativeBase):
    """Shared base for all SQLAlchemy models."""

    pass


class BaseRepository(Generic[T]):
    """
    Abstract Base Repository for SQLAlchemy 2.0.
    """

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T:
        try:
            instance = self.model(**kwargs)
            self.session.add(instance)
            await self.session.flush()
            await self.session.refresh(instance)
            return instance
        except IntegrityError as e:
            if ulog:
                ulog(
                    "database_integrity_error",
                    ok=False,
                    error=str(e.orig) if e.orig else str(e),
                    severity="ERROR",
                    model=self.model.__name__,
                )
            raise

    async def get(self, id: Any) -> T | None:
        return await self.session.get(self.model, id)

    async def list(self, limit: int = 20, offset: int = 0) -> list[T]:
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, id: Any) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    async def commit(self):
        await self.session.commit()
