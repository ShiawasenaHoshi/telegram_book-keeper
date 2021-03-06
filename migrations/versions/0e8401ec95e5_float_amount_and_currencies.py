"""float amount and currencies

Revision ID: 0e8401ec95e5
Revises: 42cfcd9370dc
Create Date: 2021-06-10 17:23:39.975191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e8401ec95e5'
down_revision = '42cfcd9370dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency',
    sa.Column('iso', sa.String(length=3), nullable=False),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('iso')
    )
    op.create_table('currency_rate',
    sa.Column('iso', sa.String(length=3), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('rate', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['iso'], ['currency.iso'], ),
    sa.PrimaryKeyConstraint('iso', 'date')
    )
    op.add_column('transaction', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.add_column('transaction', sa.Column('currency_iso', sa.String(length=3), nullable=False))
    op.alter_column('transaction', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_index('ix_tx_date', table_name='transaction')
    op.create_index('ix_tx_timestamp', 'transaction', ['timestamp'], unique=False)
    op.create_foreign_key(None, 'transaction', 'currency', ['currency_iso'], ['iso'])
    op.drop_column('transaction', 'date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transaction', sa.Column('date', sa.DATE(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'transaction', type_='foreignkey')
    op.drop_index('ix_tx_timestamp', table_name='transaction')
    op.create_index('ix_tx_date', 'transaction', ['date'], unique=False)
    op.alter_column('transaction', 'category_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('transaction', 'currency_iso')
    op.drop_column('transaction', 'timestamp')
    op.drop_table('currency_rate')
    op.drop_table('currency')
    # ### end Alembic commands ###
