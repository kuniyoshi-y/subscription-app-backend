"""add usage_logs table

Revision ID: e3c4d5e6f7a8
Revises: d2b3c4e5f6a7
Create Date: 2026-03-28 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'd2b3c4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'usage_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('expense_id', sa.UUID(), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('usage_status_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.SmallInteger(), nullable=True),
        sa.Column('is_skipped', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['expense_id'], ['expenses.id'], name='fk_usage_logs_expense_id'),
        sa.ForeignKeyConstraint(['usage_status_id'], ['usage_statuses.id'], name='fk_usage_logs_usage_status_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('expense_id', 'month', name='uq_usage_logs_expense_month'),
    )


def downgrade() -> None:
    op.drop_table('usage_logs')
