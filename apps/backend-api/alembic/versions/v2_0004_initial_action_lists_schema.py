"""Initial ActionLists Schema (Comprehensive)

Revision ID: v2_0004
Revises: v2_0003
Create Date: 2025-12-29 22:15:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'v2_0004'
down_revision: str | None = 'v2_0003'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    # --- Action Lists Table ---
    op.create_table(
        'action_lists',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('owner', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),

        # Context
        sa.Column('project_id', sa.String(length=64), nullable=True),
        sa.Column('sprint_id', sa.String(length=50), nullable=True),

        # Content
        sa.Column('items', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),

        # Metadata
        sa.Column('geometry_shape', sa.String(length=20), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),

        # Audit/Evidence
        sa.Column('evidence_refs', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('extra_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),

        # Deletion logic
        sa.Column('parent_deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('parent_deletion_note', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),

        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sprint_id'], ['sprints.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # Indexes
    op.create_index('idx_action_lists_id', 'action_lists', ['id'], unique=False)
    op.create_index('idx_action_lists_owner', 'action_lists', ['owner'], unique=False)
    op.create_index('idx_action_lists_sprint_id', 'action_lists', ['sprint_id'], unique=False)
    op.create_index('idx_action_lists_project_id', 'action_lists', ['project_id'], unique=False)
    op.create_index('idx_action_lists_project_status', 'action_lists', ['project_id', 'status'], unique=False)
    op.create_index('idx_action_lists_created_at', 'action_lists', ['created_at'], unique=False)
    op.create_index('idx_action_lists_updated_at', 'action_lists', ['updated_at'], unique=False)

    # GIN Index
    op.create_index('idx_action_lists_tags_gin', 'action_lists', ['tags'], postgresql_using='gin')

def downgrade() -> None:
    op.drop_index('idx_action_lists_tags_gin', table_name='action_lists')
    op.drop_index('idx_action_lists_updated_at', table_name='action_lists')
    op.drop_index('idx_action_lists_created_at', table_name='action_lists')
    op.drop_index('idx_action_lists_project_status', table_name='action_lists')
    op.drop_index('idx_action_lists_project_id', table_name='action_lists')
    op.drop_index('idx_action_lists_sprint_id', table_name='action_lists')
    op.drop_index('idx_action_lists_owner', table_name='action_lists')
    op.drop_index('idx_action_lists_id', table_name='action_lists')
    op.drop_table('action_lists')
