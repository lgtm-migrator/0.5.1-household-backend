"""empty message

Revision ID: 128df5b24b26
Revises: 9b5070da5d8f
Create Date: 2020-06-05 11:01:27.833369

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '128df5b24b26'
down_revision = '9b5070da5d8f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('worker_task', sa.Column('context', sa.String(length=1024), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('worker_task', 'context')
    # ### end Alembic commands ###