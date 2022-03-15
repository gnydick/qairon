"""empty message

Revision ID: 23d666e8a06e
Revises: 87b807ccb3eb
Create Date: 2022-03-14 17:07:45.824967

"""

# revision identifiers, used by Alembic.
revision = '23d666e8a06e'
down_revision = '87b807ccb3eb'

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
    op.add_column('release_artifact', sa.Column('defaults', sa.Text(), nullable=True))
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
    op.drop_column('release_artifact', 'defaults')
    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass