"""Split Trackman into a separate service

Revision ID: 08d8f92b8a83
Revises: 804fb3dc434f
Create Date: 2018-04-18 06:49:57.641015

"""

# revision identifiers, used by Alembic.
revision = '08d8f92b8a83'
down_revision = '804fb3dc434f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from trackman import db
from trackman.auth.models import UserSession


def upgrade():
    UserSession.query.delete()
    db.session.commit()

    op.drop_table('article_revision')
    op.drop_table('article')
    op.drop_table('category')
    op.drop_table('page_revision')
    op.drop_table('page')
    op.drop_table('orders')
    op.add_column('user_role', sa.Column('sub', sa.Unicode(length=255), nullable=False))
    op.drop_constraint('user_role_user_id_fkey', 'user_role', type_='foreignkey')
    op.drop_column('user_role', 'user_id')
    op.add_column('user_session', sa.Column('id_token', sa.UnicodeText(), nullable=True))
    op.add_column('user_session', sa.Column('sub', sa.Unicode(length=255), nullable=False))
    op.drop_constraint('user_session_user_id_fkey', 'user_session', type_='foreignkey')
    op.drop_column('user_session', 'user_id')
    op.drop_table('user')


def downgrade():
    op.add_column('user_session', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('user_session_user_id_fkey', 'user_session', 'user', ['user_id'], ['id'])
    op.drop_column('user_session', 'sub')
    op.drop_column('user_session', 'id_token')
    op.add_column('user_role', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('user_role_user_id_fkey', 'user_role', 'user', ['user_id'], ['id'])
    op.drop_column('user_role', 'sub')
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('user_id_seq'::regclass)"), nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('pw_hash', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('enabled', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('orders',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=12), autoincrement=False, nullable=True),
    sa.Column('placed_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('dj', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('thank_on_air', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('first_time', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('premiums', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('address1', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('address2', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('state', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('zipcode', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('amount', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('recurring', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('paid_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('shipped_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('tshirtsize', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('tshirtcolor', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('sweatshirtsize', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('method', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('custid', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('comments', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('donor_comment', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('remote_addr', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('user_agent', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='orders_pkey')
    )
    op.create_table('page',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('page_id_seq'::regclass)"), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('menu', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('html', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('published', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='page_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('article',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('article_id_seq'::regclass)"), nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('category_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('html_summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('html_content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('published', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('front_page', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], name='article_author_id_fkey'),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name='article_category_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='article_pkey'),
    sa.UniqueConstraint('slug', name='article_slug_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('page_revision',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('page_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('html', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], name='page_revision_author_id_fkey'),
    sa.ForeignKeyConstraint(['page_id'], ['page.id'], name='page_revision_page_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='page_revision_pkey')
    )
    op.create_table('article_revision',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('article_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('author_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('html_summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('html_content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], name='article_revision_article_id_fkey'),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], name='article_revision_author_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='article_revision_pkey')
    )
    op.create_table('category',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('slug', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('published', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='category_pkey')
    )
