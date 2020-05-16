"""Update user session

Change session ID to an auto-incrementing primary key and use a separate
session token field for loading sessions.

Revision ID: 32e36e5b2170
Revises: 74d71f09dd15
Create Date: 2020-05-16 22:11:22.033943

"""

# revision identifiers, used by Alembic.
revision = '32e36e5b2170'
down_revision = '74d71f09dd15'

from alembic import op
import sqlalchemy as sa

user_session_id_seq = sa.schema.Sequence('user_session_id_seq')


def upgrade():
    op.execute('DELETE FROM user_session')
    op.execute(sa.schema.CreateSequence(user_session_id_seq))
    op.alter_column(
        'user_session',
        'id',
        existing_type=sa.VARCHAR(length=255),
        type_=sa.Integer,
        postgresql_using='id::integer',
        server_default=user_session_id_seq.next_value())
    op.add_column(
        'user_session',
        sa.Column('token', sa.String(length=255), nullable=False))


def downgrade():
    op.execute('DELETE FROM user_session')
    op.alter_column(
        'user_session',
        'id',
        existing_type=sa.Integer,
        type_=sa.VARCHAR(length=255),
        server_default=None)
    op.execute(sa.schema.DropSequence(user_session_id_seq))
    op.drop_column('user_session', 'token')
