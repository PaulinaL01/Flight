"""initial

Revision ID: a88e99a3a588
Revises: 1e870a4cd909
Create Date: 2022-01-09 14:34:00.188440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a88e99a3a588'
down_revision = '1e870a4cd909'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('flight', sa.Column('departure_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('flight', sa.Column('arrival_date', sa.DateTime(timezone=True), nullable=True))
    op.drop_column('flight', 'departure_data')
    op.drop_column('flight', 'arrival_data')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('flight', sa.Column('arrival_data', sa.DATETIME(), nullable=True))
    op.add_column('flight', sa.Column('departure_data', sa.DATETIME(), nullable=True))
    op.drop_column('flight', 'arrival_date')
    op.drop_column('flight', 'departure_date')
    # ### end Alembic commands ###