"""add owner to disciplines

Revision ID: a1b2c3d4e5f6
Revises: afed8d9cf9cb
Create Date: 2026-06-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'afed8d9cf9cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'disciplines',
        sa.Column('owner_id', sa.Integer(), nullable=False, server_default='1')
    )


def downgrade() -> None:
    op.drop_column('disciplines', 'owner_id')
