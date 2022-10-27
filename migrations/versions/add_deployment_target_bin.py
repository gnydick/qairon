"""empty message

Revision ID: add_deployment_target_bin
Revises: b7c56b16a417
Create Date: 2022-08-16 11:26:34.365049

this migration will require regenerating the cascading ids across the database, this cannot be done via alembic alone,
must use the scripts/

"""

# revision identifiers, used by Alembic.
revision = 'add_deployment_target_bin'
down_revision = 'add_bin_map'

import sqlalchemy as sa
from alembic import op


def upgrade():
    upgrades_pre()
    schema_upgrades()
    upgrades_post()


def downgrade():
    downgrades_pre()
    schema_downgrades()
    downgrades_post()


def upgrades_pre():
    pass


def schema_upgrades():
    """schema upgrade migrations go here."""

    op.add_column('deployment', sa.Column('old_id', sa.String(), nullable=True))
    op.add_column('release', sa.Column('old_id', sa.String(), nullable=True))

    op.create_table('deployment_target_bin',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False, server_default='default'),
                    sa.Column('deployment_target_id', sa.String(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('last_updated_at', sa.DateTime(), nullable=True),
                    sa.Column('defaults', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['deployment_target_id'], ['deployment_target.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_deployment_target_bin_created_at'), 'deployment_target_bin', ['created_at'], unique=False)
    op.create_index(op.f('ix_deployment_target_bin_deployment_target_id'), 'deployment_target_bin',
                    ['deployment_target_id'], unique=False)
    op.create_index(op.f('ix_deployment_target_bin_last_updated_at'), 'deployment_target_bin', ['last_updated_at'],
                    unique=False)
    op.create_index(op.f('ix_deployment_target_bin_name'), 'deployment_target_bin', ['name'], unique=False)

    op.add_column('deployment', sa.Column('deployment_target_bin_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_deployment_deployment_target_bin_id'), 'deployment', ['deployment_target_bin_id'],
                    unique=False)

    op.execute("update deployment set old_id=id")
    op.execute("update release set old_id=id")

    populate_dt_bin_query = "insert into deployment_target_bin (id, deployment_target_id, name)" \
                            " select concat(bb.dt_id, ':', bb.bin), bb.dt_id, bb.bin as db_name" \
                            " from (select dt.id dt_id, bin" \
                            " from service s" \
                            " join stack st on s.stack_id = st.id" \
                            " join deployment d on d.service_id=s.id" \
                            " join deployment_target dt on dt.id=d.deployment_target_id" \
                            " join partition p on p.id =dt.partition_id" \
                            " join region r on r.id=p.region_id" \
                            " join provider pv on pv.id=r.provider_id" \
                            " left outer join bin_map b on b.env_id=pv.environment_id and b.stack_id=st.id" \
                            " group by dt_id, bin) as bb;"

    op.execute(populate_dt_bin_query)


def upgrades_post():
    op.execute(" update deployment d " \
               " set id=concat(b.db_id, ':', b.s_id, ':', b.d_tag), " \
               " deployment_target_bin_id=b.db_id " \
               " from (select concat(dt.id, ':', b.bin) as db_id, d.id as old_d_id, " \
               " dt.id dt_id, s.id s_id, d.tag d_tag, bin " \
               " from service s " \
               " join stack st on s.stack_id = st.id " \
               " join deployment d on d.service_id = s.id " \
               " join deployment_target dt on dt.id = d.deployment_target_id " \
               " join partition p on p.id = dt.partition_id " \
               " join region r on r.id = p.region_id " \
               " join provider pv on pv.id = r.provider_id " \
               " join bin_map b on b.env_id = pv.environment_id and b.stack_id = st.id " \
               " group by s.id, d.id, dt_id, d.tag, bin) as b " \
               " where d.id=b.old_d_id; ")

    remap_dep_ids()
    op.create_foreign_key('deployment_deployment_target_bin_id_fkey', 'deployment', 'deployment_target_bin',
                          ['deployment_target_bin_id'],
                          ['id'])
    # op.drop_constraint('deployment_deployment_target_id_fkey', 'deployment', type_='foreignkey')
    op.drop_column('deployment', 'deployment_target_id')
    op.drop_column('deployment', 'old_id')
    op.drop_column('release', 'old_id')


def downgrades_pre():
    op.add_column('deployment', sa.Column('old_id', sa.String(), nullable=True))
    op.add_column('release', sa.Column('old_id', sa.String(), nullable=True))
    op.execute("update deployment set old_id=id")
    op.execute("update release set old_id=id")

    op.add_column('deployment', sa.Column('deployment_target_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_foreign_key('deployment_deployment_target_id_fkey', 'deployment', 'deployment_target',
                          ['deployment_target_id'], ['id'])


def schema_downgrades():
    op.execute('update deployment as d' \
               ' set deployment_target_id=b.dt_id,' \
               ' id=concat(b.dt_id, \':\', d.service_id, \':\', d.tag)'
               ' from (select db.deployment_target_id as dt_id, ' \
               ' db.id as db_id' \
               ' from deployment_target_bin db,' \
               ' deployment d,' \
               ' deployment_target dt' \
               ' where db.deployment_target_id = dt.id) as b' \
               ' where d.deployment_target_bin_id = b.db_id;')

    remap_dep_ids()


def downgrades_post():
    # op.drop_constraint('deployment_deployment_target_bin_id_fkey', 'deployment', type_='foreignkey')
    op.drop_index(op.f('ix_deployment_deployment_target_bin_id'), table_name='deployment')
    op.drop_column('deployment', 'deployment_target_bin_id')
    op.drop_column('deployment', 'old_id')
    op.drop_column('release', 'old_id')
    op.drop_index(op.f('ix_deployment_target_bin_name'), table_name='deployment_target_bin')
    op.drop_index(op.f('ix_deployment_target_bin_last_updated_at'), table_name='deployment_target_bin')
    op.drop_index(op.f('ix_deployment_target_bin_deployment_target_id'), table_name='deployment_target_bin')
    op.drop_index(op.f('ix_deployment_target_bin_created_at'), table_name='deployment_target_bin')
    op.drop_table('deployment_target_bin')
    op.create_index(op.f('ix_deployment_deployment_target_id'), 'deployment', ['deployment_target_id'], unique=False)


# import pydevd_pycharm
# pydevd_pycharm.settrace('localhost', port=1234, stdoutToServer=True, stderrToServer=True)
def remap_dep_ids():
    op.execute('update deployment_config as dc' \
               ' set deployment_id=d.id' \
               ' from deployment as d' \
               ' where dc.deployment_id=d.old_id;'
               )

    op.execute('update deployment_proc as dp' \
               ' set deployment_id=d.id' \
               ' from deployment as d' \
               ' where dp.deployment_id=d.old_id;'
               )
    op.execute('update release as rel' \
               ' set deployment_id=d.id' \
               ' from deployment as d' \
               ' where rel.deployment_id=d.old_id;'
               )

    op.execute("update release as rel" \
               " set id=concat(rel.deployment_id, ':', rel.build_num)"
               )

    op.execute('update deployments_zones as dz' \
               ' set deployment_id=d.id' \
               ' from deployment as d' \
               ' where dz.deployment_id=d.old_id;'
               )

    op.execute("update deployment as d" \
               " set current_release_id=rel.id" \
               " from release as rel" \
               " where d.current_release_id=rel.old_id;"
               )
