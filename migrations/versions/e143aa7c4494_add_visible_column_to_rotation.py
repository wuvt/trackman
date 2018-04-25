"""add visible column to rotation

Revision ID: e143aa7c4494
Revises: 08d8f92b8a83
Create Date: 2018-04-25 04:54:55.295552

"""

# revision identifiers, used by Alembic.
revision = 'e143aa7c4494'
down_revision = '08d8f92b8a83'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('rotation', sa.Column('visible', sa.Boolean(),
                                        nullable=False,
                                        server_default=sa.literal(True)))


def downgrade():
    op.drop_column('rotation', 'visible')
