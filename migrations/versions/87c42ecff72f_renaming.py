"""renaming

Revision ID: 87c42ecff72f
Revises: 8f425d9262d3
Create Date: 2021-08-13 16:46:45.790512

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '87c42ecff72f'
down_revision = '8f425d9262d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'permission', new_column_name='access_level')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'access_level', new_column_name='permission')
    # ### end Alembic commands ###
