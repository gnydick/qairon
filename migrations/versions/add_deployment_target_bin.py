"""empty message

Revision ID: add_deployment_target_bin
Revises: b7c56b16a417
Create Date: 2022-08-16 11:26:34.365049

this migration will require regenerating the cascading ids across the database, this cannot be done via alembic alone,
must use the scripts/

"""

# revision identifiers, used by Alembic.
revision = 'add_deployment_target_bin'
down_revision = 'add_indexes'

import sqlalchemy as sa
from alembic import op

mapping = {
    'prod': {
        'withme:infra': 'bin1',
        'withme:monitoring': 'bin2',
        'withme:services': 'bin3',
    },
    'perf': {
        'withme:infra': 'bin1',
        'withme:monitoring': 'bin2'

    },
    'int': {
        'withme:infra': 'bin1',
        'withme:monitoring': 'bin2',
        'withme:services': 'bin3'

    },
    'infra':
        {
            'withme:automation': 'bin1',
            'withme:cicd': 'bin2',
            'withme:infra': 'bin3',
            'withme:monitoring': 'bin4',
            'withme:security': 'bin5'

        },
    'dev':
        {
            'kube:system': 'bin0',
            'withme:automation': 'bin1',
            'withme:cicd': 'bin2',
            'withme:devtools': 'bin3',
            'withme:infra': 'bin4',
            'withme:monitoring': 'bin5',
            'withme:resources': 'bin6',
            'withme:security': 'bin7',
            'withme:services': 'bin8'
        }
}


def upgrade():
    upgrades_pre()
    schema_upgrades()
    upgrades_post()


def downgrade():
    downgrades_pre()
    schema_downgrades()
    downgrades_post()


def upgrades_pre():
    op.create_table('bin_map',
                    sa.Column('env_id', sa.String(), nullable=False),
                    sa.Column('stack_id', sa.String(), nullable=False),
                    sa.Column('bin', sa.String(), nullable=False)
                    )


    for env, map in mapping.items():
        for ns, bin in map.items():
            op.execute("insert into bin_map (env_id, stack_id, bin) values ('%s', '%s', '%s');" % (env, ns, bin))


def schema_upgrades():
    """schema upgrade migrations go here."""

    op.add_column('deployment', sa.Column('old_id', sa.String(), nullable=True))
    op.add_column('release', sa.Column('old_id', sa.String(), nullable=True))

    op.create_table('deployment_target_bin',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False, server_default='bin0'),
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

    populate_dt_bin_query = "insert into deployment_target_bin (id, deployment_target_id, name) select concat(bb.deployment_target_id, ':', bb.bin), bb.deployment_target_id, bb.bin as db_name from (select *      from service s,      stack st,      deployment d,      deployment_target dt,      bin_map b,      partition p,      region r,      provider pv      where b.stack_id = st.id      and s.stack_id = st.id      and d.service_id = s.id      and dt.id = d.deployment_target_id      and dt.partition_id = p.id      and p.region_id = r.id      and r.provider_id = pv.id      and pv.environment_id = b.env_id) as bb;"

    op.execute(populate_dt_bin_query)




def upgrades_post():
    op.execute("update deployment as d" \
               " set deployment_target_bin_id=b.db_id," \
               " id=concat(b.db_id, ':', d.service_id, ':', d.tag)"
               " from (select db.id as db_id," \
               " dt.id as dt_id" \
               " from deployment_target_bin db," \
               " deployment_target dt" \
               " where db.deployment_target_id = dt.id) as b" \
               " where d.deployment_target_id = b.dt_id;"
               )

    remap_dep_ids()
    op.create_foreign_key('deployment_deployment_target_bin_id_fkey', 'deployment', 'deployment_target_bin',
                          ['deployment_target_bin_id'],
                          ['id'])
    # op.drop_constraint('deployment_deployment_target_id_fkey', 'deployment', type_='foreignkey')
    op.drop_column('deployment', 'deployment_target_id')
    op.drop_column('deployment', 'old_id')
    op.drop_column('release', 'old_id')

    op.drop_table('bin_map')
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
