#!/usr/bin/env python

from app import db
from models import *

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

sess = db.session()

# deployments = sess.query(Deployment).all()
#
# for dep in deployments:
#     stack = dep.service.stack_id
#     env = dep.deployment_target_bin.deployment_target.partition.region.provider.environment.id
#     print(stack)
#     print(env)
#     print()
#     print(mapping[env][stack])
#     print()

# for env, map in mapping.items():
#     print(env)
#     for ns, bin in map.items():
#         print(ns)
#         print(bin)
for env, map in mapping.items():
    for ns, bin in map.items():
        sess.execute("insert into binn_map (env_id, stack_id, bin) values ('%s', '%s', '%s');" % (env, ns, bin))


sess.commit()
sess.close()