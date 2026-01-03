"""Checklist service with checklist and template management.

Handles checklist operations including templates and item tracking.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from taskman_api.core.errors import AppError, ConflictError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.checklist import Checklist
from taskman_api.repositories.checklist_repository import ChecklistRepository
from taskman_api.schemas.checklist import (
    ChecklistCreateRequest,
    ChecklistItemAddRequest,
    ChecklistItemInput,
    ChecklistResponse,
    ChecklistUpdateRequest,
)

from .base import BaseService


def generate_checklist_id() -> str:
    """Generate a unique checklist ID with CL- prefix."""
    return f"CL-{uuid4().hex[:12].upper()}"


def generate_item_id() -> str:
    """Generate a unique item ID."""
    return f"ITEM-{uuid4().hex[:8].upper()}"


class ChecklistService(
    BaseService[Checklist, ChecklistCreateRequest, ChecklistUpdateRequest, ChecklistResponse]
):
    """Checklist business logic and operations.

    Provides checklist management including:
    - Checklist lifecycle (active, completed, archived)
    - Item management with status tracking
    - Template creation and cloning
    - Progress tracking

    Example:
        service = ChecklistService(session)
        result = await service.create(ChecklistCreateRequest(...))
        match result:
            case Ok(checklist):
                print(f"Created checklist: {checklist.id}")
            case Err(error):
                print(f"Failed: {error.message}")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ChecklistService.

        Args:
            session: Async database session
        """
        repository = ChecklistRepository(session)
        super().__init__(repository, Checklist, ChecklistResponse)
        self.checklist_repo = repository
        self.db_session = session

    async def create(
        self,
        request: ChecklistCreateRequest,
    ) -> Result[ChecklistResponse, AppError]:
        """Create new checklist.

        Generates ID and item IDs if not provided.

        Args:
            request: Checklist creation request

        Returns:
            Result containing created checklist or error
        """
        checklist_id = request.id or generate_checklist_id()

        # Process items to ensure they have IDs and order
        items = []
        for i, item in enumerate(request.items or []):
            item_data = item.model_dump()
            if not item_data.get("id"):
                item_data["id"] = generate_item_id()
            item_data["order"] = item_data.get("order", i + 1)
            item_data["status"] = item_data.get("status", "pending")
            items.append(item_data)

        # Create model
        model_data = request.model_dump()
        model_data["id"] = checklist_id
        model_data["items"] = items
        # Map metadata -> extra_metadata (SQLAlchemy reserves 'metadata')
        if "metadata" in model_data:
            model_data["extra_metadata"] = model_data.pop("metadata")
        entity = Checklist(**model_data)

        try:
            created = await self.repository.create(entity)
            response = ChecklistResponse.model_validate(created)
            return Ok(response)
        except IntegrityError as e:
            return Err(
                ConflictError(
                    message=f"A Checklist with ID '{checklist_id}' already exists",
                    entity_type="Checklist",
                    entity_id=checklist_id,
                    original_error=str(e.orig) if e.orig else str(e),
                )
            )
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def create_from_template(
        self,
        template_id: str,
        title: str | None = None,
        task_id: str | None = None,
        plan_id: str | None = None,
        conversation_id: str | None = None,
    ) -> Result[ChecklistResponse, NotFoundError | ValidationError | AppError]:
        """Create a checklist from a template.

        Args:
            template_id: Source template ID
            title: Optional override title
            task_id: Optional task association
            plan_id: Optional plan association
            conversation_id: Optional conversation association

        Returns:
            Result containing created checklist or error
        """
        # Get template
        find_result = await self.repository.find_by_id(template_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(template):
                if not template.is_template:
                    return Err(
                        ValidationError(
                            message=f"Checklist {template_id} is not a template",
                            field="template_id",
                            value=template_id,
                        )
                    )

                # Clone template items with fresh IDs
                items = []
                for i, item in enumerate(template.items or []):
                    item_data = {
                        "id": generate_item_id(),
                        "title": item.get("title"),
                        "description": item.get("description"),
                        "order": i + 1,
                        "status": "pending",
                        "priority": item.get("priority", "medium"),
                    }
                    items.append(item_data)

                # Create new checklist
                checklist = Checklist(
                    id=generate_checklist_id(),
                    title=title or f"Copy of {template.title}",
                    description=template.description,
                    status="active",
                    items=items,
                    is_template=False,
                    template_id=template_id,
                    task_id=task_id,
                    plan_id=plan_id,
                    conversation_id=conversation_id,
                    tags=template.tags.copy() if template.tags else [],
                )

                try:
                    created = await self.repository.create(checklist)
                    response = ChecklistResponse.model_validate(created)
                    return Ok(response)
                except Exception as e:
                    return Err(AppError(message=str(e)))

    async def check_item(
        self,
        checklist_id: str,
        item_id: str,
        notes: str | None = None,
    ) -> Result[ChecklistResponse, NotFoundError | ValidationError | AppError]:
        """Mark an item as completed.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier
            notes: Optional completion notes

        Returns:
            Result containing updated checklist or error
        """
        find_result = await self.repository.find_by_id(checklist_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                items = entity.items or []
                item_found = False

                for item in items:
                    if item.get("id") == item_id:
                        item_found = True
                        if item.get("status") == "completed":
                            return Err(
                                ValidationError(
                                    message="Item is already completed",
                                    field="item_id",
                                    value=item_id,
                                )
                            )

                        item["status"] = "completed"
                        item["completed_at"] = datetime.now(UTC).isoformat()
                        if notes:
                            item["notes"] = notes
                        break

                if not item_found:
                    return Err(
                        NotFoundError(
                            message=f"Item {item_id} not found in checklist",
                            entity_type="ChecklistItem",
                            entity_id=item_id,
                        )
                    )

                entity.items = items
                flag_modified(entity, "items")

                # Check if all items completed
                all_completed = all(
                    i.get("status") in ("completed", "skipped")
                    for i in items
                )
                if all_completed and items:
                    entity.status = "completed"
                    entity.completed_at = datetime.now(UTC)

                updated = await self.repository.update(entity)
                response = ChecklistResponse.model_validate(updated)
                return Ok(response)

    async def uncheck_item(
        self,
        checklist_id: str,
        item_id: str,
    ) -> Result[ChecklistResponse, NotFoundError | ValidationError | AppError]:
        """Mark a completed item as pending again.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier

        Returns:
            Result containing updated checklist or error
        """
        find_result = await self.repository.find_by_id(checklist_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                items = entity.items or []
                item_found = False

                for item in items:
                    if item.get("id") == item_id:
                        item_found = True
                        if item.get("status") != "completed":
                            return Err(
                                ValidationError(
                                    message=f"Item is not completed (current: {item.get('status')})",
                                    field="item_id",
                                    value=item_id,
                                )
                            )

                        item["status"] = "pending"
                        item.pop("completed_at", None)
                        break

                if not item_found:
                    return Err(
                        NotFoundError(
                            message=f"Item {item_id} not found in checklist",
                            entity_type="ChecklistItem",
                            entity_id=item_id,
                        )
                    )

                entity.items = items
                flag_modified(entity, "items")

                # If checklist was completed, set back to active
                if entity.status == "completed":
                    entity.status = "active"
                    entity.completed_at = None

                updated = await self.repository.update(entity)
                response = ChecklistResponse.model_validate(updated)
                return Ok(response)

    async def block_item(
        self,
        checklist_id: str,
        item_id: str,
        reason: str | None = None,
    ) -> Result[ChecklistResponse, NotFoundError | ValidationError | AppError]:
        """Mark an item as blocked.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier
            reason: Optional block reason

        Returns:
            Result containing updated checklist or error
        """
        find_result = await self.repository.find_by_id(checklist_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                items = entity.items or []
                item_found = False

                for item in items:
                    if item.get("id") == item_id:
                        item_found = True
                        if item.get("status") == "blocked":
                            return Err(
                                ValidationError(
                                    message="Item is already blocked",
                                    field="item_id",
                                    value=item_id,
                                )
                            )

                        item["status"] = "blocked"
                        item["blocked_at"] = datetime.now(UTC).isoformat()
                        if reason:
                            item["blocked_reason"] = reason
                        break

                if not item_found:
                    return Err(
                        NotFoundError(
                            message=f"Item {item_id} not found in checklist",
                            entity_type="ChecklistItem",
                            entity_id=item_id,
                        )
                    )

                entity.items = items
                flag_modified(entity, "items")

                updated = await self.repository.update(entity)
                response = ChecklistResponse.model_validate(updated)
                return Ok(response)

    async def unblock_item(
        self,
        checklist_id: str,
        item_id: str,
    ) -> Result[ChecklistResponse, NotFoundError | ValidationError | AppError]:
        """Unblock a blocked item.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier

        Returns:
            Result containing updated checklist or error
        """
        find_result = await self.repository.find_by_id(checklist_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                items = entity.items or []
                item_found = False

                for item in items:
                    if item.get("id") == item_id:
                        item_found = True
                        if item.get("status") != "blocked":
                            return Err(
                                ValidationError(
                                    message=f"Item is not blocked (current: {item.get('status')})",
                                    field="item_id",
                                    value=item_id,
                                )
                            )

                        item["status"] = "pending"
                        item.pop("blocked_at", None)
                        item.pop("blocked_reason", None)
                        break

                if not item_found:
                    return Err(
                        NotFoundError(
                            message=f"Item {item_id} not found in checklist",
                            entity_type="ChecklistItem",
                            entity_id=item_id,
                        )
                    )

                entity.items = items
                flag_modified(entity, "items")

                updated = await self.repository.update(entity)
                response = ChecklistResponse.model_validate(updated)
                return Ok(response)

    async def add_item(
        self,
        checklist_id: str,
        item: ChecklistItemInput | ChecklistItemAddRequest,
        after_item_id: str | None = None,
    ) -> Result[ChecklistResponse, NotFoundError | AppError]:
        """Add an item to a checklist.

        Args:
            checklist_id: Checklist identifier
            item: Item to add (can be ChecklistItemInput or ChecklistItemAddRequest)
            after_item_id: Insert after this item (or at end if None)

        Returns:
            Result containing updated checklist or error
        """
        find_result = await self.repository.find_by_id(checklist_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                items = entity.items or []

                # Create item data
                item_data = item.model_dump(exclude={"after_item_id"})
                item_data["id"] = item_data.get("id") or generate_item_id()
                item_data["status"] = item_data.get("status", "pending")

                # Use after_item_id from the item schema if available
                if after_item_id is None and hasattr(item, "after_item_id"):
                    after_item_id = item.after_item_id

                # Determine order
                if after_item_id:
                    # Find position to insert
                    insert_idx = len(items)
                    for i, it in enumerate(items):
                        if it.get("id") == after_item_id:
                            insert_idx = i + 1
                            break

                    # Insert and reorder
                    items.insert(insert_idx, item_data)
                    for i, it in enumerate(items):
                        it["order"] = i + 1
                else:
                    # Add at end
                    item_data["order"] = len(items) + 1
                    items.append(item_data)

                entity.items = items
                flag_modified(entity, "items")

                # If checklist was completed, set back to active
                if entity.status == "completed":
                    entity.status = "active"
                    entity.completed_at = None

                updated = await self.repository.update(entity)
                response = ChecklistResponse.model_validate(updated)
                return Ok(response)

    async def remove_item(
        self,
        checklist_id: str,
        item_id: str,
    ) -> Result[ChecklistResponse, NotFoundError | AppError]:
        """Remove an item from a checklist.

        Args:
            checklist_id: Checklist identifier
            item_id: Item identifier

        Returns:
            Result containing updated checklist or error
        """
        find_result = await self.repository.find_by_id(checklist_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                items = entity.items or []
                original_len = len(items)

                # Remove item
                items = [it for it in items if it.get("id") != item_id]

                if len(items) == original_len:
                    return Err(
                        NotFoundError(
                            message=f"Item {item_id} not found in checklist",
                            entity_type="ChecklistItem",
                            entity_id=item_id,
                        )
                    )

                # Reorder remaining items
                for i, it in enumerate(items):
                    it["order"] = i + 1

                entity.items = items
                flag_modified(entity, "items")

                # Check if all remaining items completed
                if items and all(
                    it.get("status") in ("completed", "skipped") for it in items
                ):
                    entity.status = "completed"
                    entity.completed_at = datetime.now(UTC)

                updated = await self.repository.update(entity)
                response = ChecklistResponse.model_validate(updated)
                return Ok(response)

    async def complete(
        self,
        checklist_id: str,
    ) -> Result[ChecklistResponse, NotFoundError | AppError]:
        """Mark checklist as completed.

        Args:
            checklist_id: Checklist identifier

        Returns:
            Result containing updated checklist or error
        """
        find_result = await self.repository.find_by_id(checklist_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                entity.status = "completed"
                entity.completed_at = datetime.now(UTC)

                updated = await self.repository.update(entity)
                response = ChecklistResponse.model_validate(updated)
                return Ok(response)

    async def archive(
        self,
        checklist_id: str,
    ) -> Result[ChecklistResponse, NotFoundError | AppError]:
        """Archive a checklist.

        Args:
            checklist_id: Checklist identifier

        Returns:
            Result containing updated checklist or error
        """
        update_request = ChecklistUpdateRequest(status="archived")
        return await self.update(checklist_id, update_request)

    async def search(
        self,
        status: str | None = None,
        is_template: bool | None = None,
        task_id: str | None = None,
        plan_id: str | None = None,
        conversation_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ChecklistResponse], AppError]:
        """Search checklists with filters.

        Args:
            status: Optional status filter
            is_template: Optional template filter
            task_id: Optional task filter
            plan_id: Optional plan filter
            conversation_id: Optional conversation filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing filtered checklists or error
        """
        if is_template is True:
            result = await self.checklist_repo.find_templates(limit, offset)
        elif status:
            result = await self.checklist_repo.find_by_status(status, limit, offset)
        elif task_id:
            result = await self.checklist_repo.find_by_task(
                task_id, status, limit, offset
            )
        elif plan_id:
            result = await self.checklist_repo.find_by_plan(
                plan_id, status, limit, offset
            )
        elif conversation_id:
            result = await self.checklist_repo.find_by_conversation(
                conversation_id, limit, offset
            )
        else:
            result = await self.repository.find_all(limit=limit, offset=offset)

        match result:
            case Ok(checklists):
                responses = [ChecklistResponse.model_validate(c) for c in checklists]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_templates(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ChecklistResponse], AppError]:
        """Get all checklist templates.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing templates or error
        """
        result = await self.checklist_repo.find_templates(limit, offset)

        match result:
            case Ok(checklists):
                responses = [ChecklistResponse.model_validate(c) for c in checklists]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_active(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ChecklistResponse], AppError]:
        """Get all active checklists.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing active checklists or error
        """
        result = await self.checklist_repo.find_active(limit, offset)

        match result:
            case Ok(checklists):
                responses = [ChecklistResponse.model_validate(c) for c in checklists]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_with_blocked_items(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ChecklistResponse], AppError]:
        """Get checklists with blocked items.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing checklists with blocked items or error
        """
        result = await self.checklist_repo.find_with_blocked_items(limit, offset)

        match result:
            case Ok(checklists):
                responses = [ChecklistResponse.model_validate(c) for c in checklists]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_incomplete(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ChecklistResponse], AppError]:
        """Get incomplete checklists (active with pending items).

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing incomplete checklists or error
        """
        result = await self.checklist_repo.find_incomplete(limit, offset)

        match result:
            case Ok(checklists):
                responses = [ChecklistResponse.model_validate(c) for c in checklists]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_stats(self) -> Result[dict, AppError]:
        """Get checklist statistics.

        Returns:
            Result containing stats dict or error
        """
        count_result = await self.checklist_repo.count_by_status()

        match count_result:
            case Err(error):
                return Err(error)
            case Ok(counts):
                template_result = await self.checklist_repo.count_templates()
                template_count = 0
                if isinstance(template_result, Ok):
                    template_count = template_result.value

                total = sum(counts.values())
                return Ok(
                    {
                        "total": total,
                        "templates": template_count,
                        "by_status": counts,
                    }
                )
