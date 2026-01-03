"""Conversation service with session management and turn tracking.

Handles conversation operations for agent session persistence.
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from taskman_api.core.errors import AppError, ConflictError, NotFoundError, ValidationError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.conversation import ConversationSession, ConversationTurn
from taskman_api.repositories.conversation_repository import (
    ConversationSessionRepository,
    ConversationTurnRepository,
)
from taskman_api.schemas.conversation import (
    ConversationSessionCreateRequest,
    ConversationSessionResponse,
    ConversationSessionUpdateRequest,
    ConversationTurnCreateRequest,
    ConversationTurnResponse,
)

from .base import BaseService


def generate_conversation_id() -> str:
    """Generate a unique conversation ID with CONV- prefix."""
    return f"CONV-{uuid4().hex[:12].upper()}"


def generate_turn_id() -> str:
    """Generate a unique turn ID with TURN- prefix."""
    return f"TURN-{uuid4().hex[:12].upper()}"


class ConversationSessionService(
    BaseService[
        ConversationSession,
        ConversationSessionCreateRequest,
        ConversationSessionUpdateRequest,
        ConversationSessionResponse,
    ]
):
    """Conversation session business logic.

    Provides conversation management including:
    - Session lifecycle (create, update, complete, archive)
    - Turn management with automatic sequencing
    - Token tracking and context management
    - Project/sprint association

    Example:
        service = ConversationSessionService(session)
        result = await service.create(ConversationSessionCreateRequest(...))
        match result:
            case Ok(conv):
                print(f"Created conversation: {conv.id}")
            case Err(error):
                print(f"Failed: {error.message}")
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize ConversationSessionService.

        Args:
            session: Async database session
        """
        repository = ConversationSessionRepository(session)
        super().__init__(repository, ConversationSession, ConversationSessionResponse)
        self.conv_repo = repository
        self.turn_repo = ConversationTurnRepository(session)
        self.db_session = session

    async def create(
        self,
        request: ConversationSessionCreateRequest,
    ) -> Result[ConversationSessionResponse, AppError]:
        """Create new conversation session.

        Generates ID if not provided.

        Args:
            request: Conversation creation request

        Returns:
            Result containing created conversation or error
        """
        # Generate ID if not provided
        conv_id = request.id or generate_conversation_id()

        # Create model with generated/provided ID
        model_data = request.model_dump()
        model_data["id"] = conv_id
        # Map metadata -> extra_metadata (SQLAlchemy reserves 'metadata')
        if "metadata" in model_data:
            model_data["extra_metadata"] = model_data.pop("metadata")
        entity = ConversationSession(**model_data)

        try:
            created = await self.repository.create(entity)
            response = ConversationSessionResponse.model_validate(created)
            return Ok(response)
        except IntegrityError as e:
            return Err(
                ConflictError(
                    message=f"A ConversationSession with ID '{conv_id}' already exists",
                    entity_type="ConversationSession",
                    entity_id=conv_id,
                    original_error=str(e.orig) if e.orig else str(e),
                )
            )
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def complete(
        self,
        conversation_id: str,
        summary: str | None = None,
    ) -> Result[ConversationSessionResponse, NotFoundError | AppError]:
        """Mark conversation as completed.

        Args:
            conversation_id: Conversation identifier
            summary: Optional final summary of the conversation

        Returns:
            Result containing updated conversation or error
        """
        find_result = await self.repository.find_by_id(conversation_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                entity.status = "completed"
                entity.completed_at = datetime.now(UTC)
                if summary:
                    entity.summary = summary

                try:
                    updated = await self.repository.update(entity)
                    response = ConversationSessionResponse.model_validate(updated)
                    return Ok(response)
                except Exception as e:
                    return Err(AppError(message=str(e)))

    async def pause(
        self,
        conversation_id: str,
    ) -> Result[ConversationSessionResponse, NotFoundError | AppError]:
        """Pause an active conversation.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Result containing updated conversation or error
        """
        update_request = ConversationSessionUpdateRequest(status="paused")
        return await self.update(conversation_id, update_request)

    async def resume(
        self,
        conversation_id: str,
    ) -> Result[ConversationSessionResponse, NotFoundError | ValidationError | AppError]:
        """Resume a paused conversation.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Result containing updated conversation or error
        """
        find_result = await self.repository.find_by_id(conversation_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                if entity.status not in ("paused", "active"):
                    return Err(
                        ValidationError(
                            message=f"Cannot resume conversation in '{entity.status}' status",
                            field="status",
                            value=entity.status,
                        )
                    )

                entity.status = "active"
                try:
                    updated = await self.repository.update(entity)
                    response = ConversationSessionResponse.model_validate(updated)
                    return Ok(response)
                except Exception as e:
                    return Err(AppError(message=str(e)))

    async def archive(
        self,
        conversation_id: str,
    ) -> Result[ConversationSessionResponse, NotFoundError | AppError]:
        """Archive a completed conversation.

        Args:
            conversation_id: Conversation identifier

        Returns:
            Result containing updated conversation or error
        """
        update_request = ConversationSessionUpdateRequest(status="archived")
        return await self.update(conversation_id, update_request)

    async def add_turn(
        self,
        conversation_id: str,
        request: ConversationTurnCreateRequest,
    ) -> Result[ConversationTurnResponse, NotFoundError | AppError]:
        """Add a turn to a conversation.

        Automatically assigns sequence number and updates conversation stats.

        Args:
            conversation_id: Parent conversation ID
            request: Turn creation request

        Returns:
            Result containing created turn or error
        """
        # Verify conversation exists
        conv_result = await self.repository.find_by_id(conversation_id)
        match conv_result:
            case Err(error):
                return Err(error)
            case Ok(conversation):
                pass

        # Get next sequence number
        seq_result = await self.turn_repo.get_latest_sequence(conversation_id)
        match seq_result:
            case Err(error):
                return Err(error)
            case Ok(latest_seq):
                next_seq = latest_seq + 1

        # Create turn
        turn_id = request.id or generate_turn_id()
        turn_data = request.model_dump()
        turn_data["id"] = turn_id
        turn_data["conversation_id"] = conversation_id
        turn_data["sequence"] = next_seq
        turn_data["created_at"] = datetime.now(UTC)
        # Map metadata -> extra_metadata (SQLAlchemy reserves 'metadata')
        if "metadata" in turn_data:
            turn_data["extra_metadata"] = turn_data.pop("metadata")

        turn = ConversationTurn(**turn_data)
        try:
            created_turn = await self.turn_repo.create(turn)
            # Update conversation stats
            conversation.turn_count = next_seq
            conversation.token_estimate += created_turn.token_count
            await self.repository.update(conversation)

            response = ConversationTurnResponse.model_validate(created_turn)
            return Ok(response)
        except Exception as e:
            return Err(AppError(message=str(e)))

    async def get_turns(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ConversationTurnResponse], NotFoundError | AppError]:
        """Get turns for a conversation.

        Args:
            conversation_id: Parent conversation ID
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing list of turns or error
        """
        # Verify conversation exists
        exists_result = await self.repository.exists(conversation_id)
        match exists_result:
            case Err(error):
                return Err(error)
            case Ok(False):
                return Err(
                    NotFoundError(
                        message=f"Conversation {conversation_id} not found",
                        entity_type="ConversationSession",
                        entity_id=conversation_id,
                    )
                )
            case Ok(True):
                pass

        result = await self.turn_repo.find_by_conversation(
            conversation_id, limit, offset
        )

        match result:
            case Ok(turns):
                responses = [
                    ConversationTurnResponse.model_validate(t) for t in turns
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def update_summary(
        self,
        conversation_id: str,
        summary: str,
    ) -> Result[ConversationSessionResponse, NotFoundError | AppError]:
        """Update conversation summary.

        Args:
            conversation_id: Conversation identifier
            summary: New summary text

        Returns:
            Result containing updated conversation or error
        """
        update_request = ConversationSessionUpdateRequest(summary=summary)
        return await self.update(conversation_id, update_request)

    async def link_plan(
        self,
        conversation_id: str,
        plan_id: str,
    ) -> Result[ConversationSessionResponse, NotFoundError | AppError]:
        """Link a plan to this conversation.

        Args:
            conversation_id: Conversation identifier
            plan_id: Plan ID to link

        Returns:
            Result containing updated conversation or error
        """
        find_result = await self.repository.find_by_id(conversation_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                if plan_id not in entity.plan_ids:
                    entity.plan_ids = entity.plan_ids + [plan_id]
                    flag_modified(entity, "plan_ids")

                try:
                    updated = await self.repository.update(entity)
                    response = ConversationSessionResponse.model_validate(updated)
                    return Ok(response)
                except Exception as e:
                    return Err(AppError(message=str(e)))

    async def link_checklist(
        self,
        conversation_id: str,
        checklist_id: str,
    ) -> Result[ConversationSessionResponse, NotFoundError | AppError]:
        """Link a checklist to this conversation.

        Args:
            conversation_id: Conversation identifier
            checklist_id: Checklist ID to link

        Returns:
            Result containing updated conversation or error
        """
        find_result = await self.repository.find_by_id(conversation_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                if checklist_id not in entity.checklist_ids:
                    entity.checklist_ids = entity.checklist_ids + [checklist_id]
                    flag_modified(entity, "checklist_ids")

                try:
                    updated = await self.repository.update(entity)
                    response = ConversationSessionResponse.model_validate(updated)
                    return Ok(response)
                except Exception as e:
                    return Err(AppError(message=str(e)))

    async def link_task(
        self,
        conversation_id: str,
        task_id: str,
    ) -> Result[ConversationSessionResponse, NotFoundError | AppError]:
        """Link a task to this conversation.

        Args:
            conversation_id: Conversation identifier
            task_id: Task ID to link

        Returns:
            Result containing updated conversation or error
        """
        find_result = await self.repository.find_by_id(conversation_id)

        match find_result:
            case Err(error):
                return Err(error)
            case Ok(entity):
                if task_id not in entity.task_ids:
                    entity.task_ids = entity.task_ids + [task_id]
                    flag_modified(entity, "task_ids")

                try:
                    updated = await self.repository.update(entity)
                    response = ConversationSessionResponse.model_validate(updated)
                    return Ok(response)
                except Exception as e:
                    return Err(AppError(message=str(e)))

    async def search(
        self,
        status: str | None = None,
        project_id: str | None = None,
        worktree: str | None = None,
        agent_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ConversationSessionResponse], AppError]:
        """Search conversations with filters.

        Args:
            status: Optional status filter
            project_id: Optional project filter
            worktree: Optional worktree filter
            agent_type: Optional agent type filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing filtered conversations or error
        """
        if status:
            result = await self.conv_repo.find_by_status(status, limit, offset)
        elif project_id:
            result = await self.conv_repo.find_by_project(
                project_id, status, limit, offset
            )
        elif worktree:
            result = await self.conv_repo.find_by_worktree(worktree, limit, offset)
        elif agent_type:
            result = await self.conv_repo.find_by_agent_type(agent_type, limit, offset)
        else:
            result = await self.repository.find_all(limit=limit, offset=offset)

        match result:
            case Ok(sessions):
                responses = [
                    ConversationSessionResponse.model_validate(s) for s in sessions
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_active(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[list[ConversationSessionResponse], AppError]:
        """Get all active conversations.

        Args:
            limit: Maximum results
            offset: Results to skip

        Returns:
            Result containing active conversations or error
        """
        result = await self.conv_repo.find_active(limit, offset)

        match result:
            case Ok(sessions):
                responses = [
                    ConversationSessionResponse.model_validate(s) for s in sessions
                ]
                return Ok(responses)
            case Err(error):
                return Err(error)

    async def get_stats(self) -> Result[dict, AppError]:
        """Get conversation statistics.

        Returns:
            Result containing stats dict or error
        """
        count_result = await self.conv_repo.count_by_status()

        match count_result:
            case Err(error):
                return Err(error)
            case Ok(counts):
                total = sum(counts.values())
                return Ok(
                    {
                        "total": total,
                        "by_status": counts,
                    }
                )
