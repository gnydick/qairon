"""empty message

Revision ID: b7c56b16a417
Revises: 17d1e3f964c5
Create Date: 2022-03-14 20:00:14.078059

"""

# revision identifiers, used by Alembic.
revision = 'b7c56b16a417'
down_revision = '17d1e3f964c5'

from alembic import op
import sqlalchemy as sa


from alembic import context


def upgrade():
    upgrades_pre()
    schema_upgrades()
    upgrades_post()


def downgrade():
    downgrades_pre()
    schema_downgrades()
    downgrades_post()


def upgrades_pre():
    """Add any optional data prep pre migrations here!"""
    pass


def schema_upgrades():
    """schema upgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('build_artifact', 'defaults')
    op.drop_column('release_artifact', 'defaults')
    # ### end Alembic commands ###


def upgrades_post():
    """Add any optional data prep post migrations here!"""
    pass


def downgrades_pre():
    """Add any optional data prep pre migrations here!"""
    pass


def schema_downgrades():
    """schema downgrade migrations go here."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('release_artifact', sa.Column('defaults', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('build_artifact', sa.Column('defaults', sa.TEXT(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass