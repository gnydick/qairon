"""empty message

Revision ID: add_bin_map
Revises: target_bins_fleets
Create Date: 2022-09-29 09:14:52.095312

"""

# revision identifiers, used by Alembic.
revision = "add_bin_map"
down_revision = 'add_indexes'

from alembic import op
import sqlalchemy as sa

from alembic import context

mapping = {
    'dev':
        {
            'mwebbdev:stuff': 'default',
            'withme:astral': 'dev',
            'withme:demo': 'default',
            'withme:gameserver': 'dev',
            'withme:playground': 'devplay',
            'withme:testing': 'dev',
            'withme:unreal': 'dev',
            'k8s:kube-system': 'sys',
            'kube:system': 'sys',
            'withme:automation': 'default',
            'withme:cicd': 'default',
            'withme:devtools': 'default',
            'withme:infra': 'default',
            'withme:monitoring': 'default',
            'withme:resources': 'default',
            'withme:security': 'default',
            'withme:services': 'dev'
        },
    'docs':
        {
            'app_for_docs:stack': 'default',
            'mwebbdev:stuff': 'default',
            'withme:demo': 'default'
        },
    'prod':
        {
            'k8s:kube-system': 'sys',
            'kube:system': 'sys',
            'withme:automation': 'default',
            'withme:cicd': 'default',
            'withme:devtools': 'default',
            'withme:infra': 'default',
            'withme:monitoring': 'default',
            'withme:resources': 'default',
            'withme:security': 'default',
            'withme:services': 'withmeprod',
            'withme:astral': 'withmeprod',
            'withme:gameserver': 'withmeprod',
            'withme:testing': 'withmeprod'
        },
    'perf':
        {
            'k8s:kube-system': 'sys',
            'kube:system': 'sys',
            'withme:automation': 'default',
            'withme:cicd': 'default',
            'withme:devtools': 'default',
            'withme:infra': 'default',
            'withme:monitoring': 'default',
            'withme:resources': 'default',
            'withme:security': 'default',
            'withme:services': 'withmeperf',
            'withme:gameserver': 'withmeperf',
            'withme:testing': 'withmeperf'

        },
    'int':
        {
            'withme:gameserver': 'withmedev',
            'withme:testing': 'withmedev',
            'k8s:kube-system': 'sys',
            'kube:system': 'sys',
            'withme:automation': 'default',
            'withme:cicd': 'default',
            'withme:devtools': 'default',
            'withme:infra': 'default',
            'withme:monitoring': 'default',
            'withme:resources': 'default',
            'withme:security': 'default',
            'withme:services': 'withmedev'

        },
    'infra':
        {
            'k8s:kube-system': 'sys',
            'kube:system': 'sys',
            'withme:automation': 'default',
            'withme:cicd': 'default',
            'withme:devtools': 'default',
            'withme:infra': 'default',
            'withme:monitoring': 'default',
            'withme:resources': 'default',
            'withme:security': 'default',

        },
    'legacy':
        {
            'withme:astral': 'default',
            'withme:cicd': 'default',
            'withme:gameserver': 'default',
            'withme:playground': 'default',
            'withme:services': 'default'
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
    """Add any optional data prep pre migrations here!"""
    pass


def schema_upgrades():
    op.create_table('bin_map',
                    sa.Column('env_id', sa.String(), nullable=False),
                    sa.Column('stack_id', sa.String(), nullable=False),
                    sa.Column('bin', sa.String(), nullable=False)
                    )

    for env, map in mapping.items():
        for ns, bin in map.items():
            op.execute("insert into bin_map (env_id, stack_id, bin) values ('%s', '%s', '%s');" % (env, ns, bin))


def upgrades_post():
    """Add any optional data prep post migrations here!"""
    pass


def downgrades_pre():
    """Add any optional data prep pre migrations here!"""
    pass


def schema_downgrades():
    op.drop_table('bin_map')


def downgrades_post():
    """Add any optional data prep post migrations here!"""
    pass
