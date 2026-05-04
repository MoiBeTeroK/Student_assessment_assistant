"""recreate_update_exam_results

Revision ID: fb08ccb3af83
Revises: cabd242561fc
Create Date: 2026-05-04 16:46:55.162658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb08ccb3af83'
down_revision: Union[str, Sequence[str], None] = 'cabd242561fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'audio',
        sa.Column('id_audio', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('id_question', sa.Integer(), nullable=False),
        sa.Column('id_result', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id_audio'),
        sa.ForeignKeyConstraint(['id_question'], ['questions.id_question'], ),
        sa.ForeignKeyConstraint(['id_result'], ['exam_results.id_result'], )
    )
    op.create_index(op.f('ix_audio_id_audio'), 'audio', ['id_audio'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audio_id_audio'), table_name='audio')
    op.drop_table('audio')
