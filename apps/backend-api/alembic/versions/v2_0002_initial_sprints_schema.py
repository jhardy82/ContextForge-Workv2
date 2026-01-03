"""Initial Sprints Schema (Comprehensive)

Revision ID: v2_0002
Revises: v2_0001
Create Date: 2025-12-29 22:05:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "v2_0002"
down_revision: str | None = "v2_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SPRINT_PHASES_JSON = '{"planning": {"status": "not_started", "has_sprint_goal": false, "has_capacity_plan": false, "tasks_estimated": false}, "implementation": {"status": "not_started", "progress_pct": 0, "tasks_completed": 0, "tasks_total": 0}}'


def upgrade() -> None:
    # --- Sprints Table ---
    op.create_table(
        "sprints",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("goal", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("start_date", sa.String(length=20), nullable=True),
        sa.Column("end_date", sa.String(length=20), nullable=True),
        sa.Column("primary_project", sa.String(length=64), nullable=True),  # FK
        # Comprehensive Columns
        sa.Column("cadence", sa.String(length=20), nullable=True),
        sa.Column("owner", sa.String(length=100), nullable=True),
        sa.Column(
            "tasks", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
        sa.Column(
            "imported_tasks",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("velocity_target_points", sa.Float(), nullable=True),
        sa.Column("actual_points", sa.Float(), nullable=True),
        sa.Column("carried_over_points", sa.Float(), nullable=True),
        sa.Column(
            "definition_of_done",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "scope_changes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"
        ),
        sa.Column("timezone", sa.String(length=50), nullable=True),
        sa.Column(
            "observability",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "phases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text(f"'{SPRINT_PHASES_JSON}'::jsonb"),
        ),
        sa.Column("pending_reason", sa.String(length=500), nullable=True),
        sa.Column("blocked_reason", sa.String(length=500), nullable=True),
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
        sa.ForeignKeyConstraint(["primary_project"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes
    op.create_index("idx_sprints_id", "sprints", ["id"], unique=False)
    op.create_index("idx_sprints_primary_project", "sprints", ["primary_project"], unique=False)
    op.create_index("idx_sprints_owner", "sprints", ["owner"], unique=False)
    op.create_index("idx_sprints_start_date", "sprints", ["start_date"], unique=False)
    op.create_index("idx_sprints_end_date", "sprints", ["end_date"], unique=False)
    op.create_index(
        "idx_sprints_project_status", "sprints", ["primary_project", "status"], unique=False
    )
    op.create_index("idx_sprints_created_at", "sprints", ["created_at"], unique=False)
    op.create_index("idx_sprints_updated_at", "sprints", ["updated_at"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_sprints_updated_at", table_name="sprints")
    op.drop_index("idx_sprints_created_at", table_name="sprints")
    op.drop_index("idx_sprints_project_status", table_name="sprints")
    op.drop_index("idx_sprints_end_date", table_name="sprints")
    op.drop_index("idx_sprints_start_date", table_name="sprints")
    op.drop_index("idx_sprints_owner", table_name="sprints")
    op.drop_index("idx_sprints_primary_project", table_name="sprints")
    op.drop_index("idx_sprints_id", table_name="sprints")
    op.drop_table("sprints")
