"""Conversation repository with session and turn queries.

Provides specialized queries for conversation session tracking.
"""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from taskman_api.core.errors import DatabaseError
from taskman_api.core.result import Err, Ok, Result
from taskman_api.models.conversation import ConversationSession, ConversationTurn

from .base import BaseRepository


class ConversationSessionRepository(BaseRepository[ConversationSession]):
    """Repository for ConversationSession with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = ConversationSessionRepository(session)
            sessions = await repo.find_active()
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize conversation session repository.

        Args:
            session: Async database session
        """
        super().__init__(ConversationSession, session)

    async def find_by_status(
        self,
        status: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationSession], DatabaseError]:
        """Find sessions by status.

        Args:
            status: Session status (active, paused, completed, archived)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sessions or error
        """
        try:
            stmt = (
                select(ConversationSession)
                .where(ConversationSession.status == status)
                .order_by(ConversationSession.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            return Ok(sessions)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sessions by status {status}",
                    operation="find_by_status",
                    details=str(e),
                )
            )

    async def find_active(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationSession], DatabaseError]:
        """Find all active sessions.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of active sessions or error
        """
        return await self.find_by_status("active", limit, offset)

    async def find_by_project(
        self,
        project_id: str,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationSession], DatabaseError]:
        """Find sessions by project with optional status filter.

        Args:
            project_id: Project ID to filter by
            status: Optional status filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sessions or error
        """
        try:
            stmt = select(ConversationSession).where(
                ConversationSession.project_id == project_id
            )

            if status is not None:
                stmt = stmt.where(ConversationSession.status == status)

            stmt = (
                stmt.order_by(ConversationSession.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )

            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            return Ok(sessions)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sessions by project {project_id}",
                    operation="find_by_project",
                    details=str(e),
                )
            )

    async def find_by_worktree(
        self,
        worktree: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationSession], DatabaseError]:
        """Find sessions by worktree.

        Args:
            worktree: Git worktree name to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sessions or error
        """
        try:
            stmt = (
                select(ConversationSession)
                .where(ConversationSession.worktree == worktree)
                .order_by(ConversationSession.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            return Ok(sessions)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sessions by worktree {worktree}",
                    operation="find_by_worktree",
                    details=str(e),
                )
            )

    async def find_by_agent_type(
        self,
        agent_type: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationSession], DatabaseError]:
        """Find sessions by agent type.

        Args:
            agent_type: Agent/model type to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of sessions or error
        """
        try:
            stmt = (
                select(ConversationSession)
                .where(ConversationSession.agent_type == agent_type)
                .order_by(ConversationSession.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            return Ok(sessions)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sessions by agent_type {agent_type}",
                    operation="find_by_agent_type",
                    details=str(e),
                )
            )

    async def find_recent(
        self,
        days: int = 7,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationSession], DatabaseError]:
        """Find sessions created or updated in the last N days.

        Args:
            days: Number of days to look back
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of recent sessions or error
        """
        try:
            cutoff = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            from datetime import timedelta

            cutoff = cutoff - timedelta(days=days)

            stmt = (
                select(ConversationSession)
                .where(ConversationSession.updated_at >= cutoff)
                .order_by(ConversationSession.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            return Ok(sessions)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find sessions from last {days} days",
                    operation="find_recent",
                    details=str(e),
                )
            )

    async def find_with_high_token_count(
        self,
        min_tokens: int = 50000,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationSession], DatabaseError]:
        """Find sessions with high token counts (approaching context limits).

        Args:
            min_tokens: Minimum token estimate threshold
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of high-token sessions or error
        """
        try:
            stmt = (
                select(ConversationSession)
                .where(ConversationSession.token_estimate >= min_tokens)
                .order_by(ConversationSession.token_estimate.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            sessions = result.scalars().all()
            return Ok(sessions)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find high-token sessions (>={min_tokens})",
                    operation="find_with_high_token_count",
                    details=str(e),
                )
            )

    async def count_by_status(self) -> Result[dict[str, int], DatabaseError]:
        """Get count of sessions grouped by status.

        Returns:
            Result with dict of status -> count or error
        """
        try:
            stmt = select(
                ConversationSession.status,
                func.count(ConversationSession.id).label("count"),
            ).group_by(ConversationSession.status)

            result = await self.session.execute(stmt)
            rows = result.all()
            counts = {row.status: row.count for row in rows}
            return Ok(counts)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message="Failed to count sessions by status",
                    operation="count_by_status",
                    details=str(e),
                )
            )


class ConversationTurnRepository(BaseRepository[ConversationTurn]):
    """Repository for ConversationTurn with specialized queries.

    Example:
        ```python
        async with get_db() as session:
            repo = ConversationTurnRepository(session)
            turns = await repo.find_by_conversation("CONV-001")
        ```
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize conversation turn repository.

        Args:
            session: Async database session
        """
        super().__init__(ConversationTurn, session)

    async def find_by_conversation(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationTurn], DatabaseError]:
        """Find turns by conversation ID ordered by sequence.

        Args:
            conversation_id: Parent conversation ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of turns or error
        """
        try:
            stmt = (
                select(ConversationTurn)
                .where(ConversationTurn.conversation_id == conversation_id)
                .order_by(ConversationTurn.sequence.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            turns = result.scalars().all()
            return Ok(turns)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find turns for conversation {conversation_id}",
                    operation="find_by_conversation",
                    details=str(e),
                )
            )

    async def find_by_role(
        self,
        conversation_id: str,
        role: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationTurn], DatabaseError]:
        """Find turns by conversation and role.

        Args:
            conversation_id: Parent conversation ID
            role: Role to filter by (user, assistant, system, tool)
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of turns or error
        """
        try:
            stmt = (
                select(ConversationTurn)
                .where(
                    ConversationTurn.conversation_id == conversation_id,
                    ConversationTurn.role == role,
                )
                .order_by(ConversationTurn.sequence.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            turns = result.scalars().all()
            return Ok(turns)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find {role} turns for {conversation_id}",
                    operation="find_by_role",
                    details=str(e),
                )
            )

    async def find_summaries(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationTurn], DatabaseError]:
        """Find summary turns for a conversation.

        Args:
            conversation_id: Parent conversation ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of summary turns or error
        """
        try:
            stmt = (
                select(ConversationTurn)
                .where(
                    ConversationTurn.conversation_id == conversation_id,
                    ConversationTurn.is_summary == True,  # noqa: E712
                )
                .order_by(ConversationTurn.sequence.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            turns = result.scalars().all()
            return Ok(turns)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find summaries for {conversation_id}",
                    operation="find_summaries",
                    details=str(e),
                )
            )

    async def find_with_tool_calls(
        self,
        conversation_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Result[Sequence[ConversationTurn], DatabaseError]:
        """Find turns with tool calls for a conversation.

        Args:
            conversation_id: Parent conversation ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Result with list of turns with tool calls or error
        """
        try:
            # JSONB query for non-empty tool_calls array
            stmt = (
                select(ConversationTurn)
                .where(
                    ConversationTurn.conversation_id == conversation_id,
                    func.jsonb_array_length(ConversationTurn.tool_calls) > 0,
                )
                .order_by(ConversationTurn.sequence.asc())
                .limit(limit)
                .offset(offset)
            )
            result = await self.session.execute(stmt)
            turns = result.scalars().all()
            return Ok(turns)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to find tool-call turns for {conversation_id}",
                    operation="find_with_tool_calls",
                    details=str(e),
                )
            )

    async def get_latest_sequence(
        self,
        conversation_id: str,
    ) -> Result[int, DatabaseError]:
        """Get the latest sequence number for a conversation.

        Args:
            conversation_id: Parent conversation ID

        Returns:
            Result with latest sequence number (0 if no turns) or error
        """
        try:
            stmt = select(func.max(ConversationTurn.sequence)).where(
                ConversationTurn.conversation_id == conversation_id
            )
            result = await self.session.execute(stmt)
            max_seq = result.scalar()
            return Ok(max_seq or 0)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to get latest sequence for {conversation_id}",
                    operation="get_latest_sequence",
                    details=str(e),
                )
            )

    async def count_by_conversation(
        self,
        conversation_id: str,
    ) -> Result[int, DatabaseError]:
        """Count turns in a conversation.

        Args:
            conversation_id: Parent conversation ID

        Returns:
            Result with turn count or error
        """
        try:
            stmt = select(func.count(ConversationTurn.id)).where(
                ConversationTurn.conversation_id == conversation_id
            )
            result = await self.session.execute(stmt)
            count = result.scalar() or 0
            return Ok(count)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to count turns for {conversation_id}",
                    operation="count_by_conversation",
                    details=str(e),
                )
            )

    async def get_token_total(
        self,
        conversation_id: str,
    ) -> Result[int, DatabaseError]:
        """Get total token count for a conversation.

        Args:
            conversation_id: Parent conversation ID

        Returns:
            Result with total tokens or error
        """
        try:
            stmt = select(func.sum(ConversationTurn.token_count)).where(
                ConversationTurn.conversation_id == conversation_id
            )
            result = await self.session.execute(stmt)
            total = result.scalar() or 0
            return Ok(total)
        except SQLAlchemyError as e:
            return Err(
                DatabaseError(
                    message=f"Failed to get token total for {conversation_id}",
                    operation="get_token_total",
                    details=str(e),
                )
            )

    async def delete_by_conversation(
        self,
        conversation_id: str,
    ) -> Result[int, DatabaseError]:
        """Delete all turns for a conversation.

        Args:
            conversation_id: Parent conversation ID

        Returns:
            Result with number of deleted turns or error
        """
        try:
            from sqlalchemy import delete

            # First count for return value
            count_result = await self.count_by_conversation(conversation_id)
            if isinstance(count_result, Err):
                return count_result

            count = count_result.value

            stmt = delete(ConversationTurn).where(
                ConversationTurn.conversation_id == conversation_id
            )
            await self.session.execute(stmt)
            await self.session.flush()
            return Ok(count)
        except SQLAlchemyError as e:
            await self.session.rollback()
            return Err(
                DatabaseError(
                    message=f"Failed to delete turns for {conversation_id}",
                    operation="delete_by_conversation",
                    details=str(e),
                )
            )
