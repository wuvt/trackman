"""add claim tables

Revision ID: bca03d9f623f
Revises: e143aa7c4494
Create Date: 2018-04-26 07:13:41.446740

"""

# revision identifiers, used by Alembic.
revision = 'bca03d9f623f'
down_revision = 'e143aa7c4494'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('dj_claim',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dj_id', sa.Integer(), nullable=True),
    sa.Column('sub', sa.Unicode(length=255), nullable=False),
    sa.ForeignKeyConstraint(['dj_id'], ['dj.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dj_claim_token',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dj_id', sa.Integer(), nullable=True),
    sa.Column('sub', sa.Unicode(length=255), nullable=False),
    sa.Column('email', sa.Unicode(length=255), nullable=True),
    sa.Column('token', sa.Unicode(length=255), nullable=True),
    sa.Column('request_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['dj_id'], ['dj.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('dj_claim_token')
    op.drop_table('dj_claim')
