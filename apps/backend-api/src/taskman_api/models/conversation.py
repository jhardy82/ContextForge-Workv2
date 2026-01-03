"""Conversation Session and Turn ORM models.

Provides persistent conversation tracking across agent sessions.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from taskman_api.db.base import Base, TimestampMixin


class ConversationSession(Base, TimestampMixin):
    """SQLAlchemy model for conversation sessions.

    Tracks complete conversations with context persistence.
    """

    __tablename__ = "conversation_sessions"

    # Identity
    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        doc="Unique conversation ID (prefer CONV-* prefix)",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable title",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        doc="Conversation status: active, paused, completed, archived",
    )

    # Context
    agent_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default="claude",
        doc="Model/agent identifier",
    )

    worktree: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="Git worktree if applicable",
    )

    project_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Associated TaskMan project",
    )

    sprint_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="Associated sprint",
    )

    # State
    turn_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Number of turns in conversation",
    )

    token_estimate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Estimated tokens consumed",
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Rolling context summary",
    )

    # Metadata
    tags: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Tags for categorization",
    )

    extra_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Flexible key-value storage",
    )

    # Relationships
    plan_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Associated plan IDs",
    )

    checklist_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Associated checklist IDs",
    )

    task_ids: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Related task IDs",
    )

    # Completion
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when conversation was completed",
    )

    __table_args__ = (
        Index("idx_conv_sessions_status", "status"),
        Index("idx_conv_sessions_project", "project_id"),
        Index("idx_conv_sessions_created", "created_at"),
    )

    @property
    def is_active(self) -> bool:
        """Check if conversation is active."""
        return self.status == "active"

    @property
    def is_completed(self) -> bool:
        """Check if conversation is completed."""
        return self.status == "completed"


class ConversationTurn(Base):
    """SQLAlchemy model for conversation turns.

    Individual turns within a conversation.
    """

    __tablename__ = "conversation_turns"

    # Identity
    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        doc="Turn ID (prefer TURN-* prefix)",
    )

    conversation_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="Parent conversation ID",
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Turn number in conversation",
    )

    # Content
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Role: user, assistant, system, tool",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Turn content",
    )

    content_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="text",
        doc="Content type: text, tool_call, tool_result, summary",
    )

    # Tool usage
    tool_calls: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Tools invoked this turn",
    )

    tool_results: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        doc="Tool execution results",
    )

    # Analysis
    token_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Estimated token count",
    )

    is_summary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="True if this is a context summary",
    )

    # Metadata
    extra_metadata: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        doc="Additional metadata",
    )

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when turn was created",
    )

    __table_args__ = (
        Index("idx_conv_turns_conv_seq", "conversation_id", "sequence"),
    )
