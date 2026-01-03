"""Initial Projects Schema (Comprehensive)

Revision ID: v2_0001
Revises:
Create Date: 2025-12-29 22:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "v2_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# JSON defaults
PROJECT_PHASES_JSON = '{"research": {"status": "not_started", "has_market_research": false, "has_technical_research": false, "research_adequate": false}, "planning": {"status": "not_started", "has_prd": false, "has_architecture": false, "has_roadmap": false}}'


def upgrade() -> None:
    # --- Projects Table ---
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("mission", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("owner", sa.String(length=100), nullable=True),
        sa.Column("start_date", sa.String(length=20), nullable=True),
        # Comprehensive/New Columns
        sa.Column(
            "sprints", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
        sa.Column(
            "team_members",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "labels", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
        sa.Column(
            "observability_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "phases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text(f"'{PROJECT_PHASES_JSON}'::jsonb"),
        ),
        sa.Column("pending_reason", sa.String(length=500), nullable=True),
        sa.Column("blocked_reason", sa.String(length=500), nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes
    op.create_index("idx_projects_id", "projects", ["id"], unique=False)
    op.create_index("idx_projects_owner", "projects", ["owner"], unique=False)
    op.create_index("idx_projects_start_date", "projects", ["start_date"], unique=False)
    op.create_index("idx_projects_created_at", "projects", ["created_at"], unique=False)
    op.create_index("idx_projects_updated_at", "projects", ["updated_at"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_projects_updated_at", table_name="projects")
    op.drop_index("idx_projects_created_at", table_name="projects")
    op.drop_index("idx_projects_start_date", table_name="projects")
    op.drop_index("idx_projects_owner", table_name="projects")
    op.drop_index("idx_projects_id", table_name="projects")
    op.drop_table("projects")
