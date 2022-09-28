"""empty message

Revision ID: cf0de342e94f
Revises: add_deployment_target_bin
Create Date: 2022-08-22 18:42:53.529171

"""

# revision identifiers, used by Alembic.
revision = 'target_bins_fleets'
down_revision = 'add_deployment_target_bin'

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
    op.create_table('target_bins_fleets',
    sa.Column('deployment_target_bin_id', sa.String(), nullable=True),
    sa.Column('fleet_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_target_bin_id'], ['deployment_target_bin.id'], ),
    sa.ForeignKeyConstraint(['fleet_id'], ['fleet.id'], )
    )
    op.create_index('ix_target_bins_to_fleets_deployment_target_bin_id', 'target_bins_fleets', ['deployment_target_bin_id'], unique=False)
    op.create_index('ix_target_bins_to_fleets_fleet_id', 'target_bins_fleets', ['fleet_id'], unique=False)
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
    op.drop_index('ix_target_bins_to_fleets_fleet_id', table_name='target_bins_fleets')
    op.drop_index('ix_target_bins_to_fleets_deployment_target_bin_id', table_name='target_bins_fleets')
    op.drop_table('target_bins_fleets')
    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass