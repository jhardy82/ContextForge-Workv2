"""Initial Tasks Schema (Comprehensive)

Revision ID: v2_0003
Revises: v2_0002
Create Date: 2025-12-29 22:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "v2_0003"
down_revision: str | None = "v2_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TASK_PHASES_JSON = '{"research": {"status": "not_started", "has_research": false, "research_adequate": false}, "planning": {"status": "not_started", "has_acceptance_criteria": false, "has_definition_of_done": false}, "implementation": {"status": "not_started", "progress_pct": 0, "has_code_changes": false}, "testing": {"status": "not_started", "has_unit_tests": false, "tests_passing": false}}'


def upgrade() -> None:
    # --- Tasks Table ---
    op.create_table(
        "tasks",
        sa.Column("id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),  # e.g., 'todo', 'in_progress'
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("owner", sa.String(length=100), nullable=False),
        # Foreign Keys
        sa.Column("primary_project", sa.String(length=64), nullable=False),
        sa.Column("primary_sprint", sa.String(length=50), nullable=False),
        # Comprehensive Fields
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "assignees",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column(
            "related_projects",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "related_sprints",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        # Estimates
        sa.Column("estimate_points", sa.Float(), nullable=True),
        sa.Column("actual_time_hours", sa.Float(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        # Dependencies/Relations
        sa.Column(
            "parents", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
        sa.Column(
            "depends_on",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "blocks", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
        sa.Column(
            "blockers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
        # Validation
        sa.Column(
            "acceptance_criteria",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "definition_of_done",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "quality_gates",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "verification",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "actions_taken",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "related_links",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        # ContextForge Workflow
        sa.Column("shape", sa.String(length=20), nullable=True),
        sa.Column("stage", sa.String(length=50), nullable=True),
        sa.Column("work_type", sa.String(length=50), nullable=True),
        sa.Column("work_stream", sa.String(length=100), nullable=True),
        # Metrics
        sa.Column("business_value_score", sa.Integer(), nullable=True),
        sa.Column("cost_of_delay_score", sa.Integer(), nullable=True),
        sa.Column("automation_candidate", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("cycle_time_days", sa.Float(), nullable=True),
        # Risks & Obs
        sa.Column(
            "risks", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"
        ),
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
            server_default=sa.text(f"'{TASK_PHASES_JSON}'::jsonb"),
        ),
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
        sa.ForeignKeyConstraint(["primary_project"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["primary_sprint"], ["sprints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes
    op.create_index("idx_tasks_id", "tasks", ["id"], unique=False)
    op.create_index("idx_tasks_status", "tasks", ["status"], unique=False)
    op.create_index("idx_tasks_priority", "tasks", ["priority"], unique=False)
    op.create_index("idx_tasks_owner", "tasks", ["owner"], unique=False)
    op.create_index("idx_tasks_primary_project", "tasks", ["primary_project"], unique=False)
    op.create_index("idx_tasks_primary_sprint", "tasks", ["primary_sprint"], unique=False)
    op.create_index("idx_tasks_status_priority", "tasks", ["status", "priority"], unique=False)
    op.create_index(
        "idx_tasks_project_status", "tasks", ["primary_project", "status"], unique=False
    )
    op.create_index("idx_tasks_sprint_status", "tasks", ["primary_sprint", "status"], unique=False)
    op.create_index("idx_tasks_created_at", "tasks", ["created_at"], unique=False)
    op.create_index("idx_tasks_updated_at", "tasks", ["updated_at"], unique=False)

    # GIN Indexes (JSONB search)
    op.create_index("idx_tasks_assignees_gin", "tasks", ["assignees"], postgresql_using="gin")
    op.create_index(
        "idx_tasks_labels_gin", "tasks", ["related_links"], postgresql_using="gin"
    )  # using related_links as generic labels often
    op.create_index("idx_tasks_depends_on_gin", "tasks", ["depends_on"], postgresql_using="gin")
    op.create_index("idx_tasks_blocks_gin", "tasks", ["blocks"], postgresql_using="gin")


def downgrade() -> None:
    op.drop_index("idx_tasks_blocks_gin", table_name="tasks")
    op.drop_index("idx_tasks_depends_on_gin", table_name="tasks")
    op.drop_index("idx_tasks_labels_gin", table_name="tasks")
    op.drop_index("idx_tasks_assignees_gin", table_name="tasks")

    op.drop_index("idx_tasks_updated_at", table_name="tasks")
    op.drop_index("idx_tasks_created_at", table_name="tasks")
    op.drop_index("idx_tasks_sprint_status", table_name="tasks")
    op.drop_index("idx_tasks_project_status", table_name="tasks")
    op.drop_index("idx_tasks_status_priority", table_name="tasks")
    op.drop_index("idx_tasks_primary_sprint", table_name="tasks")
    op.drop_index("idx_tasks_primary_project", table_name="tasks")
    op.drop_index("idx_tasks_owner", table_name="tasks")
    op.drop_index("idx_tasks_priority", table_name="tasks")
    op.drop_index("idx_tasks_status", table_name="tasks")
    op.drop_index("idx_tasks_id", table_name="tasks")

    op.drop_table("tasks")
