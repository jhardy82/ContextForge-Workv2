"""Generic base service for CRUD operations.

Provides reusable business logic layer between repositories and API endpoints.
"""

from typing import Generic, TypeVar

from taskman_api.core.errors import AppError, NotFoundError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.db.repositories.base import BaseRepository

TModel = TypeVar("TModel")  # SQLAlchemy model type
TCreate = TypeVar("TCreate")  # Pydantic create request schema
TUpdate = TypeVar("TUpdate")  # Pydantic update request schema
TResponse = TypeVar("TResponse")  # Pydantic response schema


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

    async def create(
        self,
        request: TCreate,
    ) -> Result[TResponse, AppError]:
        """Create new entity from validated request.

        Args:
            request: Validated create request schema

        Returns:
            Result containing created entity response or error

        Example:
            request = TaskCreateRequest(id="T-001", title="New Task", ...)
            result = await service.create(request)
            match result:
                case Ok(task_response):
                    print(f"Created task: {task_response.id}")
                case Err(error):
                    print(f"Failed: {error.message}")
        """
        # Convert Pydantic schema to ORM model (include default values)
        model_data = request.model_dump()
        entity = self.model_class(**model_data)

        # Repository operation
        result = await self.repository.create(entity)

        # Convert ORM model to response schema
        match result:
            case Ok(created_entity):
                response = self.response_class.model_validate(created_entity)
                return Ok(response)
            case Err(error):
                return Err(error)

    async def get(
        self,
        entity_id: str,
    ) -> Result[TResponse, NotFoundError | AppError]:
        """Get entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result containing entity response or error

        Example:
            result = await service.get("T-001")
            match result:
                case Ok(task_response):
                    print(f"Found task: {task_response.title}")
                case Err(NotFoundError() as error):
                    print(f"Not found: {error.entity_id}")
        """
        result = await self.repository.find_by_id(entity_id)

        match result:
            case Ok(entity):
                response = self.response_class.model_validate(entity)
                return Ok(response)
            case Err(error):
                return Err(error)

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

        Example:
            update_request = TaskUpdateRequest(status=TaskStatus.IN_PROGRESS)
            result = await service.update("T-001", update_request)
            match result:
                case Ok(task_response):
                    print(f"Updated task status: {task_response.status}")
                case Err(error):
                    print(f"Update failed: {error.message}")
        """
        # Get existing entity
        find_result = await self.repository.find_by_id(entity_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                # Apply partial updates (only set fields that were provided)
                update_data = request.model_dump(exclude_unset=True)
                for field, value in update_data.items():
                    setattr(entity, field, value)

                # Save updated entity
                update_result = await self.repository.update(entity)

                match update_result:
                    case Ok(updated_entity):
                        response = self.response_class.model_validate(updated_entity)
                        return Ok(response)
                    case Err(error):
                        return Err(error)

    async def delete(
        self,
        entity_id: str,
    ) -> Result[bool, NotFoundError | AppError]:
        """Delete entity by ID.

        Args:
            entity_id: Entity identifier

        Returns:
            Result containing True if deleted, or error

        Example:
            result = await service.delete("T-001")
            match result:
                case Ok(True):
                    print("Task deleted successfully")
                case Err(NotFoundError()):
                    print("Task not found")
        """
        return await self.repository.delete(entity_id)

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

        Example:
            # Get first 50 tasks
            result = await service.list(limit=50, offset=0)
            match result:
                case Ok(tasks):
                    print(f"Found {len(tasks)} tasks")
                case Err(error):
                    print(f"Query failed: {error.message}")
        """
        result = await self.repository.find_all(limit=limit, offset=offset)

        match result:
            case Ok(entities):
                responses = [
                    self.response_class.model_validate(entity)
                    for entity in entities
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def exists(
        self,
        entity_id: str,
    ) -> Result[bool, AppError]:
        """Check if entity exists.

        Args:
            entity_id: Entity identifier

        Returns:
            Result containing True if exists, False otherwise, or error

        Example:
            result = await service.exists("T-001")
            match result:
                case Ok(True):
                    print("Task exists")
                case Ok(False):
                    print("Task does not exist")
        """
        return await self.repository.exists(entity_id)

    async def count(self) -> Result[int, AppError]:
        """Count total entities.

        Returns:
            Result containing total count or error

        Example:
            result = await service.count()
            match result:
                case Ok(count):
                    print(f"Total tasks: {count}")
                case Err(error):
                    print(f"Count failed: {error.message}")
        """
        return await self.repository.count()
