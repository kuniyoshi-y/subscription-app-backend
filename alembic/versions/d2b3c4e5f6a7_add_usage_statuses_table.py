"""add usage_statuses table

Revision ID: d2b3c4e5f6a7
Revises: c1a2b3d4e5f6
Create Date: 2026-03-28 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd2b3c4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'c1a2b3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'usage_statuses',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=False),
        sa.Column('label', sa.String(length=50), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.bulk_insert(
        sa.table(
            'usage_statuses',
            sa.column('id', sa.Integer),
            sa.column('label', sa.String),
            sa.column('score', sa.Integer),
        ),
        [
            {'id': 1, 'label': 'よく使う',    'score': 3},
            {'id': 2, 'label': 'たまに',      'score': 2},
            {'id': 3, 'label': '使ってない',  'score': 1},
        ],
    )


def downgrade() -> None:
    op.drop_table('usage_statuses')
