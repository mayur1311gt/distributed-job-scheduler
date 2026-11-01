"""create job tables

Revision ID: 0001
Revises: 
Create Date: 2026-11-01 16:00:25.630905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('job_definitions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('cron_expression', sa.String(length=100), nullable=False),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('catch_up_policy', sa.String(length=20), server_default='SKIP', nullable=False),
    sa.Column('max_retries', sa.Integer(), server_default='3', nullable=False),
    sa.Column('next_run_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('job_runs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('job_id', sa.UUID(), nullable=False),
    sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('attempt', sa.Integer(), server_default='1', nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['job_definitions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('job_id', 'scheduled_for', name='uq_job_runs_job_id_scheduled_for')
    )
    op.create_index('idx_job_runs_status', 'job_runs', ['status', 'scheduled_for'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_job_runs_status', table_name='job_runs')
    op.drop_table('job_runs')
    op.drop_table('job_definitions')
