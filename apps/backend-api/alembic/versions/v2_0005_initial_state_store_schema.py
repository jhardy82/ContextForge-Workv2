"""Initial StateStore Schema (Comprehensive)

Revision ID: v2_0005
Revises: v2_0004
Create Date: 2025-12-29 22:20:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'v2_0005'
down_revision: str | None = 'v2_0004'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    # --- Conversation Sessions ---
    op.create_table(
        "conversation_sessions",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("agent_type", sa.String(50), nullable=True, server_default="claude"),
        sa.Column("worktree", sa.String(100), nullable=True),
        sa.Column("project_id", sa.String(50), nullable=True),
        sa.Column("sprint_id", sa.String(50), nullable=True),
        sa.Column("turn_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("token_estimate", sa.Integer, nullable=False, server_default="0"),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("plan_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("checklist_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("task_ids", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_conv_sessions_status", "conversation_sessions", ["status"])
    op.create_index("idx_conv_sessions_project", "conversation_sessions", ["project_id"])
    op.create_index("idx_conv_sessions_created", "conversation_sessions", ["created_at"])

    # --- Conversation Turns ---
    op.create_table(
        "conversation_turns",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("conversation_id", sa.String(100), nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("content_type", sa.String(20), nullable=False, server_default="text"),
        sa.Column("tool_calls", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("tool_results", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("token_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_summary", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_conv_turns_conv_id", "conversation_turns", ["conversation_id"])
    op.create_index("idx_conv_turns_conv_seq", "conversation_turns", ["conversation_id", "sequence"])

    # --- Plans ---
    op.create_table(
        "plans",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("conversation_id", sa.String(100), nullable=True),
        sa.Column("project_id", sa.String(50), nullable=True),
        sa.Column("sprint_id", sa.String(50), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_plans_status", "plans", ["status"])
    op.create_index("idx_plans_conv", "plans", ["conversation_id"])
    op.create_index("idx_plans_project", "plans", ["project_id"])

    # --- Checklists ---
    op.create_table(
        "checklists",
        sa.Column("id", sa.String(100), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("items", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("conversation_id", sa.String(100), nullable=True),
        sa.Column("plan_id", sa.String(100), nullable=True),
        sa.Column("task_id", sa.String(50), nullable=True),
        sa.Column("is_template", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("template_id", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("extra_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_checklists_status", "checklists", ["status"])
    op.create_index("idx_checklists_template", "checklists", ["is_template"])
    op.create_index("idx_checklists_task", "checklists", ["task_id"])
    op.create_index("idx_checklists_plan", "checklists", ["plan_id"])

def downgrade() -> None:
    op.drop_table("checklists")
    op.drop_table("plans")
    op.drop_table("conversation_turns")
    op.drop_table("conversation_sessions")
