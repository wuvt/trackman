"""Add track metadata to TrackLog table

Revision ID: 74d71f09dd15
Revises: bca03d9f623f
Create Date: 2018-04-30 04:39:24.604922

"""

# revision identifiers, used by Alembic.
revision = '74d71f09dd15'
down_revision = 'bca03d9f623f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('tracklog', sa.Column('album', sa.Unicode(length=255), nullable=True))
    op.add_column('tracklog', sa.Column('artist', sa.Unicode(length=255), nullable=True))
    op.add_column('tracklog', sa.Column('label', sa.Unicode(length=255), nullable=True))
    op.add_column('tracklog', sa.Column('title', sa.Unicode(length=500), nullable=True))
    op.create_index(op.f('ix_tracklog_artist'), 'tracklog', ['artist'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_tracklog_artist'), table_name='tracklog')
    op.drop_column('tracklog', 'title')
    op.drop_column('tracklog', 'label')
    op.drop_column('tracklog', 'artist')
    op.drop_column('tracklog', 'album')
