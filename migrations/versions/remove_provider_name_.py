"""empty message

Revision ID: remove_provider_name
Revises: mv_env_to_prov
Create Date: 2021-10-09 18:04:01.251626

"""

# revision identifiers, used by Alembic.
revision = 'remove_provider_name'
down_revision = 'mv_env_to_prov'

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
    op.drop_column('provider', 'name')
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
    op.add_column('provider', sa.Column('name', sa.VARCHAR(), server_default=sa.text("''::character varying"), autoincrement=False, nullable=False))
    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass