"""drop receipt table

Revision ID: d4e8f1a2b3c5
Revises: 0c01cfce0c7c
Create Date: 2026-09-10 15:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e8f1a2b3c5'
down_revision = '0c01cfce0c7c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('receipt')


def downgrade():
    op.create_table(
        'receipt',
        sa.Column('tx_id', sa.Integer(), nullable=False),
        sa.Column('file_number', sa.SmallInteger(), nullable=False),
        sa.Column('msg_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['tx_id'], ['transaction.id']),
        sa.PrimaryKeyConstraint('tx_id', 'file_number'),
    )
    op.create_index('ix_receipt_msg_id', 'receipt', ['msg_id'], unique=False)
