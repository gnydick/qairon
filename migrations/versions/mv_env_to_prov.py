"""empty message

Revision ID: mv_env_to_prov
Revises: build_vcs_ref
Create Date: 2021-10-09 14:16:09.538776

"""

# revision identifiers, used by Alembic.
revision = 'mv_env_to_prov'
down_revision = 'build_vcs_ref'

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
    # op.execute("SET session_replication_role = 'replica';")
    pass


def schema_upgrades():
    delete_query = 'delete from environment e where id in (select e.id from environment e ' \
                   'left outer join deployment_target dt on e.id = dt.environment_id where dt.id is null);'

    update_query = 'update provider as p' \
                   ' set environment_id=q.eid' \
                   ' from (select dt.environment_id as eid, p.id as pid' \
                   ' from deployment_target dt,' \
                   ' partition prt,' \
                   ' region r,' \
                   ' provider p,' \
                   ' environment e' \
                   ' where r.provider_id = p.id' \
                   ' and prt.region_id = r.id' \
                   ' and dt.partition_id = prt.id' \
                   ' and dt.environment_id = e.id) as q' \
                   ' where p.id = q.pid;'

    op.execute(delete_query)
    op.add_column('provider', sa.Column('environment_id', sa.String(), nullable=True))
    op.execute(update_query)
    op.execute("update provider set environment_id='legacy' where environment_id is null")
    op.alter_column('provider', 'environment_id', nullable=False)
    op.create_foreign_key('provider_environment_id_fkey', 'provider', 'environment', ['environment_id'], ['id'], onupdate='CASCADE')
    op.drop_constraint('deployment_target_environment_id_fkey', 'deployment_target', type_='foreignkey')
    op.drop_column('deployment_target', 'environment_id')


def upgrades_post():
    # op.execute("SET session_replication_role = 'origin';")
    pass


def downgrades_pre():
    # op.execute("SET session_replication_role = 'replica';")
    pass

def schema_downgrades():
    """schema downgrade migrations go here."""
    downgrade_query = 'update deployment_target as dt ' \
                      'set environment_id=q.eid ' \
                      'from (select p.environment_id as eid, dt.id as dtid ' \
                      'from deployment_target dt, ' \
                      'partition prt, ' \
                      'region r, ' \
                      'provider p, ' \
                      'environment e ' \
                      'where r.provider_id = p.id ' \
                      'and prt.region_id = r.id ' \
                      'and dt.partition_id = prt.id ' \
                      'and p.environment_id = e.id) as q ' \
                      'where q.dtid=dt.id '

    op.add_column('deployment_target', sa.Column('environment_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.execute(downgrade_query)
    op.alter_column('deployment_target', 'environment_id', nullable=False)
    op.create_foreign_key('deployment_target_environment_id_fkey', 'deployment_target', 'environment',
                          ['environment_id'], ['id'], onupdate='CASCADE')
    op.drop_constraint('provider_environment_id_fkey', 'provider', type_='foreignkey')
    op.drop_column('provider', 'environment_id')


def downgrades_post():
    # op.execute("SET session_replication_role = 'origin';")
    pass
