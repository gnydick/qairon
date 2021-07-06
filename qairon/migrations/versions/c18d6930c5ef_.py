"""empty message

Revision ID: c18d6930c5ef
Revises: 3729e673db6a
Create Date: 2021-07-06 10:37:18.048892

"""

# revision identifiers, used by Alembic.
revision = 'c18d6930c5ef'
down_revision = '3729e673db6a'

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
    op.drop_constraint('config_template_config_template_type_id_fkey', 'config_template', type_='foreignkey')
    op.drop_table('config_template_type')
    op.drop_column('config_template', 'version')
    op.drop_column('config_template', 'config_template_type_id')
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
    op.create_table('config_template_type',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('defaults', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='config_template_type_pkey')
    )
    op.add_column('config_template', sa.Column('config_template_type_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('config_template', sa.Column('version', sa.VARCHAR(), autoincrement=False, nullable=False, server_default='1', default='1'))
    op.create_foreign_key('config_template_config_template_type_id_fkey', 'config_template', 'config_template_type', ['config_template_type_id'], ['id'])

    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass