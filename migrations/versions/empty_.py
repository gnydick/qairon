"""empty message

Revision ID: empty
Revises: None
Create Date: 2021-10-05 16:33:01.598088

"""

# revision identifiers, used by Alembic.
revision = 'empty'
down_revision = None

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
    pass


def upgrades_post():
    """Add any optional data prep post migrations here!"""
    pass


def downgrades_pre():
    """Add any optional data prep pre migrations here!"""
    pass


def schema_downgrades():
    """schema downgrade migrations go here."""
    pass


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass