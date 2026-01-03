"""Generic base service for CRUD operations.

Provides reusable business logic layer between repositories and API endpoints.
"""

import json
from typing import Any, Generic, TypeVar

import structlog
from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from taskman_api.core.errors import AppError, ConflictError, DatabaseError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.base import Base
from taskman_api.repositories.base import BaseRepository

logger = structlog.get_logger(__name__)

TModel = TypeVar("TModel", bound=Base)  # SQLAlchemy model type
TCreate = TypeVar("TCreate", bound=BaseModel)  # Pydantic create request schema
TUpdate = TypeVar("TUpdate", bound=BaseModel)  # Pydantic update request schema
TResponse = TypeVar("TResponse", bound=BaseModel)  # Pydantic response schema


class BaseService(Generic[TModel, TCreate, TUpdate, TResponse]):
    """Generic service layer with business logic.

    Coordinates between repositories and schemas.
    Provides CRUD operations with Result monad pattern.

    Type Parameters:
        TModel: SQLAlchemy ORM model type
        TCreate: Pydantic schema for create requests
        TUpdate: Pydantic schema for update requests (partial)
        TResponse: Pydantic schema for responses

    Example:
        class TaskService(BaseService[Task, TaskCreateRequest, TaskUpdateRequest, TaskResponse]):
            def __init__(self, session: AsyncSession):
                repository = TaskRepository(session)
                super().__init__(repository, Task, TaskResponse)
    """

    def __init__(
        self,
        repository: BaseRepository[TModel],
        model_class: type[TModel],
        response_class: type[TResponse],
    ) -> None:
        """Initialize service with repository and schema classes.

        Args:
            repository: Repository instance for data access
            model_class: SQLAlchemy model class for entity
            response_class: Pydantic response schema class
        """
        self.repository = repository
        self.model_class = model_class
        self.response_class = response_class

    def _serialize_json_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """Serialize list/dict fields to JSON strings for SQLite compatibility.

        Inspects the model to find columns that might need serialization.
        Currently serializes ALL list/dict values found in data if they map to a column.
        """
        mapper = inspect(self.model_class)
        valid_columns = set(mapper.columns.keys())

        serialized_data = {}
        for key, value in data.items():
            if key in valid_columns:
                # Auto-serialize lists and dicts to JSON strings
                if isinstance(value, (list, dict)):
                    try:
                        serialized_data[key] = json.dumps(value)
                    except (TypeError, ValueError):
                        # Fallback if not serializable
                        serialized_data[key] = value
                else:
                    serialized_data[key] = value
        return serialized_data

    def _deserialize_json_fields(self, entity: TModel) -> dict[str, Any]:
        """Deserialize JSON strings back to list/dict for Pydantic validation.

        Converts entity to dict and attempts to parse JSON strings.
        """
        # Convert entity to dict, excluding internal SQLAlchemy state
        data = {k: v for k, v in entity.__dict__.items() if not k.startswith("_")}

        mapper = inspect(self.model_class)
        valid_columns = set(mapper.columns.keys())

        deserialized_data = data.copy()

        for key, value in data.items():
            if key in valid_columns and isinstance(value, str):
                stripped = value.strip()
                # Heuristic check for JSON array or object
                if (stripped.startswith("{") and stripped.endswith("}")) or (
                    stripped.startswith("[") and stripped.endswith("]")
                ):
                    try:
                        deserialized_data[key] = json.loads(value)
                    except json.JSONDecodeError:
                        # Keep original string if not valid JSON
                        pass

        return deserialized_data

    async def create(
        self,
        request: TCreate,
    ) -> Result[TResponse, AppError]:
        """Create new entity from validated request.

        Args:
            request: Validated create request schema

        Returns:
            Result containing created entity response or error
        """
        try:
            logger.debug(
                "service.create.start",
                model=self.model_class.__name__,
                request_data=request.model_dump(mode="json"),
            )
            # Convert Pydantic schema to dict (mode='json' ensures Enums -> str)
            model_data = request.model_dump(mode="json")

            # Serialize JSON fields for DB
            db_data = self._serialize_json_fields(model_data)

            # Create entity
            entity = self.model_class(**db_data)

            # Repository operation
            created_entity = await self.repository.create(entity)

            # Deserialize JSON fields for response
            response_data = self._deserialize_json_fields(created_entity)

            # Convert to response schema
            response = self.response_class.model_validate(response_data)
            logger.debug(
                "service.create.success", model=self.model_class.__name__, response_id=response.id
            )
            return Ok(response)
        except IntegrityError as e:
            return Err(
                ConflictError(
                    message=f"A {self.model_class.__name__} with this identifier already exists",
                    entity_type=self.model_class.__name__,
                    original_error=str(e.orig) if e.orig else str(e),
                )
            )
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def get(
        self,
        entity_id: str,
    ) -> Result[TResponse, NotFoundError | AppError]:
        """Get entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result containing entity response or error
        """
        try:
            entity = await self.repository.get_by_id(entity_id)

            if entity is None:
                return Err(
                    NotFoundError(
                        message=f"{self.model_class.__name__} not found: {entity_id}",
                        entity_id=entity_id,
                        entity_type=self.model_class.__name__,
                    )
                )

            # Deserialize JSON fields for response
            response_data = self._deserialize_json_fields(entity)

            response = self.response_class.model_validate(response_data)
            return Ok(response)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def update(
        self,
        entity_id: str,
        request: TUpdate,
    ) -> Result[TResponse, NotFoundError | AppError]:
        """Update entity with partial fields.

        Only fields provided in the request are updated.
        Missing fields retain their current values.

        Args:
            entity_id: Entity identifier
            request: Validated update request schema (partial)

        Returns:
            Result containing updated entity response or error
        """
        try:
            logger.debug(
                "service.update.start", model=self.model_class.__name__, entity_id=entity_id
            )
            # Get existing entity
            entity = await self.repository.get_by_id(entity_id)

            if entity is None:
                return Err(
                    NotFoundError(
                        message=f"{self.model_class.__name__} not found: {entity_id}",
                        entity_id=entity_id,
                        entity_type=self.model_class.__name__,
                    )
                )

            # Apply partial updates (only set fields that were provided)
            update_data = request.model_dump(exclude_unset=True, mode="json")

            # Serialize JSON fields for DB
            # Note: We only serialize fields present in update_data
            serialized_update_data = self._serialize_json_fields(update_data)

            for field, value in serialized_update_data.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)

            # Save updated entity
            updated_entity = await self.repository.update(entity)

            # Deserialize JSON fields for response
            response_data = self._deserialize_json_fields(updated_entity)

            response = self.response_class.model_validate(response_data)
            return Ok(response)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def delete(
        self,
        entity_id: str,
    ) -> Result[bool, NotFoundError | DatabaseError]:
        """Delete entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result containing True if deleted, or error
        """
        try:
            entity = await self.repository.get_by_id(entity_id)

            if entity is None:
                return Err(
                    NotFoundError(
                        message=f"{self.model_class.__name__} not found: {entity_id}",
                        entity_id=entity_id,
                        entity_type=self.model_class.__name__,
                    )
                )

            await self.repository.delete(entity)
            logger.debug(
                "service.delete.success", model=self.model_class.__name__, entity_id=entity_id
            )
            return Ok(True)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[TResponse], AppError]:
        """List entities with pagination.

        Args:
            limit: Maximum number of results (default: 100, max: 1000)
            offset: Number of results to skip (default: 0)

        Returns:
            Result containing list of entity responses or error
        """
        try:
            entities = await self.repository.get_all(limit=limit, offset=offset)

            # Deserialize JSON fields for each entity
            responses = []
            for e in entities:
                response_data = self._deserialize_json_fields(e)
                responses.append(self.response_class.model_validate(response_data))

            logger.debug(
                "service.list.success", model=self.model_class.__name__, count=len(responses)
            )
            return Ok(responses)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def exists(
        self,
        entity_id: str,
    ) -> Result[bool, DatabaseError]:
        """Check if entity exists.

        Args:
            entity_id: Entity identifier

        Returns:
            Result containing True if exists, False otherwise, or error
        """
        try:
            exists = await self.repository.exists(entity_id)
            return Ok(exists)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def count(self) -> Result[int, DatabaseError]:
        """Count total entities.

        Returns:
            Result containing total count or error
        """
        try:
            count = await self.repository.count()
            return Ok(count)
        except Exception as e:
            return Err(AppError(message=str(e)))
