"""empty message

Revision ID: 5b5cfcb6df33
Revises: None
Create Date: 2021-03-16 13:29:35.101348

"""

# revision identifiers, used by Alembic.
revision = '5b5cfcb6df33'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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
    op.create_table('allocation_type',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('unit', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('application',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('config_template_type',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deployment_target_type',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('environment',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('language',
    sa.Column('id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pop_type',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('repo_type',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('config_template',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('version', sa.String(), nullable=False),
    sa.Column('config_template_type_id', sa.String(), nullable=True),
    sa.Column('doc', sa.Text(), nullable=False),
    sa.Column('language_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['config_template_type_id'], ['config_template_type.id'], ),
    sa.ForeignKeyConstraint(['language_id'], ['language.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fleet_type',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('pop_type_id', sa.String(), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['pop_type_id'], ['pop_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pop',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('pop_type_id', sa.String(), nullable=False),
    sa.Column('native', sa.Text(), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['pop_type_id'], ['pop_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('repo',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('repo_type_id', sa.String(), nullable=True),
    sa.Column('url', sa.String(length=253), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['repo_type_id'], ['repo_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stack',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('application_id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['application_id'], ['application.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('region',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('pop_id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.Column('native', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['pop_id'], ['pop.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('service',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('stack_id', sa.String(), nullable=False),
    sa.Column('repo_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('scm_url', sa.String(), nullable=True),
    sa.Column('artifact_name', sa.String(), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['repo_id'], ['repo.id'], ),
    sa.ForeignKeyConstraint(['stack_id'], ['stack.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('build',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('build_num', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_updated_at', sa.DateTime(), nullable=False),
    sa.Column('service_id', sa.String(), nullable=False),
    sa.Column('git_tag', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('partition',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('region_id', sa.String(), nullable=False),
    sa.Column('native', sa.Text(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('proc',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('service_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('service_config',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('config_template_id', sa.String(), nullable=True),
    sa.Column('service_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('tag', sa.String(), nullable=False),
    sa.Column('config', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['config_template_id'], ['config_template.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('zone',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('region_id', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.Column('native', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['region_id'], ['region.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deployment_target',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('deployment_target_type_id', sa.String(), nullable=True),
    sa.Column('partition_id', sa.String(), nullable=True),
    sa.Column('environment_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.Column('native', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_target_type_id'], ['deployment_target_type.id'], ),
    sa.ForeignKeyConstraint(['environment_id'], ['environment.id'], ),
    sa.ForeignKeyConstraint(['partition_id'], ['partition.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('network',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('partition_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('cidr', postgresql.CIDR(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.Column('native', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['partition_id'], ['partition.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deployment',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('deployment_target_id', sa.String(), nullable=True),
    sa.Column('service_id', sa.String(), nullable=True),
    sa.Column('tag', sa.String(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_target_id'], ['deployment_target.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['service.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fleet',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('deployment_target_id', sa.String(), nullable=True),
    sa.Column('fleet_type_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.Column('native', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_target_id'], ['deployment_target.id'], ),
    sa.ForeignKeyConstraint(['fleet_type_id'], ['fleet_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subnet',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('network_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('cidr', postgresql.CIDR(), nullable=False),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.Column('native', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['network_id'], ['network.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('capacity',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('fleet_id', sa.String(), nullable=True),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('allocation_type_id', sa.String(), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['allocation_type_id'], ['allocation_type.id'], ),
    sa.ForeignKeyConstraint(['fleet_id'], ['fleet.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deployment_config',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('config_template_id', sa.String(), nullable=True),
    sa.Column('deployment_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('tag', sa.String(), nullable=False),
    sa.Column('config', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['config_template_id'], ['config_template.id'], ),
    sa.ForeignKeyConstraint(['deployment_id'], ['deployment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deployment_proc',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('deployment_id', sa.String(), nullable=True),
    sa.Column('proc_id', sa.String(), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_id'], ['deployment.id'], ),
    sa.ForeignKeyConstraint(['proc_id'], ['proc.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('deployments_zones',
    sa.Column('deployment_id', sa.String(), nullable=True),
    sa.Column('zone_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_id'], ['deployment.id'], ),
    sa.ForeignKeyConstraint(['zone_id'], ['zone.id'], )
    )
    op.create_table('release',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('build_id', sa.String(), nullable=False),
    sa.Column('deployment_id', sa.String(), nullable=False),
    sa.Column('build_num', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], ),
    sa.ForeignKeyConstraint(['deployment_id'], ['deployment.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subnets_fleets',
    sa.Column('subnet_id', sa.String(), nullable=True),
    sa.Column('fleet_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['fleet_id'], ['fleet.id'], ),
    sa.ForeignKeyConstraint(['subnet_id'], ['subnet.id'], )
    )
    op.create_table('allocation',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('value', sa.Float(), nullable=False),
    sa.Column('allocation_type_id', sa.String(), nullable=True),
    sa.Column('deployment_proc_id', sa.String(), nullable=True),
    sa.Column('watermark', sa.Enum('HIGH', 'LOW', name='watermark'), nullable=True),
    sa.Column('defaults', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['allocation_type_id'], ['allocation_type.id'], ),
    sa.ForeignKeyConstraint(['deployment_proc_id'], ['deployment_proc.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('current_dep_release',
    sa.Column('deployment_id', sa.String(), nullable=True),
    sa.Column('release_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['deployment_id'], ['deployment.id'], ),
    sa.ForeignKeyConstraint(['release_id'], ['release.id'], ),
    sa.UniqueConstraint('deployment_id')
    )
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
    op.drop_table('current_dep_release')
    op.drop_table('allocation')
    op.drop_table('subnets_fleets')
    op.drop_table('release')
    op.drop_table('deployments_zones')
    op.drop_table('deployment_proc')
    op.drop_table('deployment_config')
    op.drop_table('capacity')
    op.drop_table('subnet')
    op.drop_table('fleet')
    op.drop_table('deployment')
    op.drop_table('network')
    op.drop_table('deployment_target')
    op.drop_table('zone')
    op.drop_table('service_config')
    op.drop_table('proc')
    op.drop_table('partition')
    op.drop_table('build')
    op.drop_table('service')
    op.drop_table('region')
    op.drop_table('stack')
    op.drop_table('repo')
    op.drop_table('pop')
    op.drop_table('fleet_type')
    op.drop_table('config_template')
    op.drop_table('repo_type')
    op.drop_table('pop_type')
    op.drop_table('language')
    op.drop_table('environment')
    op.drop_table('deployment_target_type')
    op.drop_table('config_template_type')
    op.drop_table('application')
    op.drop_table('allocation_type')
    # ### end Alembic commands ###


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass