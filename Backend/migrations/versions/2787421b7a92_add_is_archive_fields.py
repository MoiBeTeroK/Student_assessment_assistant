"""add_is_archive_fields

Revision ID: 2787421b7a92
Revises: a1b2c3d4e5f6
Create Date: 2026-06-14 17:51:42.009309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2787421b7a92'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('questions', sa.Column('is_archive', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('students', sa.Column('is_archive', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.add_column('tests', sa.Column('is_archive', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tests', 'is_archive')
    op.drop_column('students', 'is_archive')
    op.drop_column('questions', 'is_archive')
    
    # ### end Alembic commands ###