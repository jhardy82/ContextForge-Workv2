"""Conversation and Turn Pydantic schemas.

Request/response schemas for conversation tracking API endpoints.
Supports session persistence across context limits.
"""

from datetime import datetime
from typing import Literal

from pydantic import Field

from .base import BaseSchema, TimestampSchema


# Status type aliases
ConversationStatus = Literal["active", "paused", "completed", "archived"]
TurnRole = Literal["user", "assistant", "system", "tool"]
TurnContentType = Literal["text", "tool_call", "tool_result", "summary"]


# ============================================================================
# Conversation Session Schemas
# ============================================================================


class ConversationSessionCreateRequest(BaseSchema):
    """Schema for creating a new conversation session."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique conversation ID, prefer CONV-* prefix",
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Human-readable title",
    )

    # Context
    agent_type: str = Field(
        default="claude",
        max_length=50,
        description="Model/agent identifier",
    )

    worktree: str | None = Field(
        default=None,
        max_length=100,
        description="Git worktree if applicable",
    )

    project_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated TaskMan project",
    )

    sprint_id: str | None = Field(
        default=None,
        max_length=50,
        description="Associated sprint",
    )

    # Metadata
    tags: list[str] = Field(
        default_factory=list,
        description="Tags for categorization",
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value storage",
    )

    # Relationships
    plan_ids: list[str] = Field(
        default_factory=list,
        description="Associated plan IDs",
    )

    checklist_ids: list[str] = Field(
        default_factory=list,
        description="Associated checklist IDs",
    )

    task_ids: list[str] = Field(
        default_factory=list,
        description="Related task IDs",
    )


class ConversationSessionUpdateRequest(BaseSchema):
    """Schema for updating an existing conversation session.

    All fields are optional for partial updates.
    """

    title: str | None = Field(default=None, min_length=1, max_length=255)
    status: ConversationStatus | None = None
    agent_type: str | None = Field(default=None, max_length=50)
    worktree: str | None = Field(default=None, max_length=100)
    project_id: str | None = Field(default=None, max_length=50)
    sprint_id: str | None = Field(default=None, max_length=50)

    # State updates
    turn_count: int | None = Field(default=None, ge=0)
    token_estimate: int | None = Field(default=None, ge=0)
    summary: str | None = None

    # Metadata
    tags: list[str] | None = None
    metadata: dict | None = None

    # Relationships
    plan_ids: list[str] | None = None
    checklist_ids: list[str] | None = None
    task_ids: list[str] | None = None


class ConversationSessionResponse(TimestampSchema):
    """Schema for conversation session API responses."""

    model_config = {"from_attributes": True, "populate_by_name": True}

    id: str
    title: str
    status: ConversationStatus

    # Context
    agent_type: str | None
    worktree: str | None
    project_id: str | None
    sprint_id: str | None

    # State
    turn_count: int
    token_estimate: int
    summary: str | None

    # Metadata
    tags: list[str]
    # Note: SQLAlchemy reserves 'metadata', so ORM uses 'extra_metadata'
    metadata: dict = Field(validation_alias="extra_metadata")

    # Relationships
    plan_ids: list[str]
    checklist_ids: list[str]
    task_ids: list[str]

    # Completion
    completed_at: datetime | None


# ============================================================================
# Conversation Turn Schemas
# ============================================================================


class ConversationTurnCreateRequest(BaseSchema):
    """Schema for creating a new conversation turn."""

    id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Turn ID, prefer TURN-* prefix",
    )

    conversation_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Parent conversation ID",
    )

    sequence: int = Field(
        ...,
        ge=1,
        description="Turn number in conversation",
    )

    # Content
    role: TurnRole = Field(
        ...,
        description="Role of the turn (user/assistant/system/tool)",
    )

    content: str = Field(
        ...,
        min_length=1,
        description="Turn content",
    )

    content_type: TurnContentType = Field(
        default="text",
        description="Content type",
    )

    # Tool usage
    tool_calls: list[dict] = Field(
        default_factory=list,
        description="Tools invoked this turn",
    )

    tool_results: list[dict] = Field(
        default_factory=list,
        description="Tool execution results",
    )

    # Analysis
    token_count: int = Field(
        default=0,
        ge=0,
        description="Estimated token count",
    )

    is_summary: bool = Field(
        default=False,
        description="True if this is a context summary",
    )

    # Metadata
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata",
    )


class ConversationTurnResponse(BaseSchema):
    """Schema for conversation turn API responses."""

    model_config = {"from_attributes": True, "populate_by_name": True}

    id: str
    conversation_id: str
    sequence: int

    role: TurnRole
    content: str
    content_type: TurnContentType

    tool_calls: list[dict]
    tool_results: list[dict]

    token_count: int
    is_summary: bool

    # Note: SQLAlchemy reserves 'metadata', so ORM uses 'extra_metadata'
    metadata: dict = Field(validation_alias="extra_metadata")
    created_at: datetime


class ConversationTurnListResponse(BaseSchema):
    """Schema for listing conversation turns."""

    turns: list[ConversationTurnResponse]
    total: int
    conversation_id: str


# ============================================================================
# Conversation List/Filter Schemas
# ============================================================================


class ConversationListResponse(BaseSchema):
    """Schema for listing conversations."""

    conversations: list[ConversationSessionResponse]
    total: int


class ConversationSummaryRequest(BaseSchema):
    """Schema for requesting conversation summarization."""

    max_tokens: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Maximum tokens for summary",
    )

    include_tool_calls: bool = Field(
        default=False,
        description="Include tool call summaries",
    )


class ConversationSummaryResponse(BaseSchema):
    """Schema for conversation summary response."""

    conversation_id: str
    summary: str
    token_count: int
    turns_summarized: int
