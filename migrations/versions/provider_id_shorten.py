"""empty message

Revision ID: provider_id_shorten
Revises: mv_env_to_prov
Create Date: 2021-10-09 17:29:23.323801

"""

# revision identifiers, used by Alembic.
revision = '20f6600fee55'
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
    op.add_column('provider', sa.Column('index', sa.String(), nullable=True))
    op.execute("update provider set index='0000'")
    op.execute("update provider set native_id='000000000000' where native_id is null")
    op.alter_column('provider', 'index', nullable=False)
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
    op.drop_column('provider', 'index')
    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass