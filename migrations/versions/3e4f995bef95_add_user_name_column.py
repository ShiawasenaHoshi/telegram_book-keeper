"""add user.name column

Revision ID: 3e4f995bef95
Revises: 87c42ecff72f
Create Date: 2021-08-14 19:19:56.435769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e4f995bef95'
down_revision = '87c42ecff72f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_bot_state')
    op.add_column('user', sa.Column('name', sa.String(length=240), default="noname"))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'name')
    op.create_table('user_bot_state',
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('state', sa.VARCHAR(length=48), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='user_bot_state_user_id_fkey'),
    sa.PrimaryKeyConstraint('user_id', name='user_bot_state_pkey')
    )
    # ### end Alembic commands ###
