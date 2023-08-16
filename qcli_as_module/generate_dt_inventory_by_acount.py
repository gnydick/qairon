import collections
import json
import sys
from pathlib import Path

from controllers import *

PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)
eks_clusters = dict()


def file(obj):
    (_, _, account_id, _, _) = obj['partition_id'].split(':')

    if account_id not in eks_clusters.keys():
        eks_clusters[account_id] = list()
    eks_clusters[account_id].append(obj['name'])


results = []

ioc = IterableOutputController(results)

cli = CLIController(ioc)
rest = RestController()

ioc.handle(data=cli.query('deployment_target',
                          query='[{"name": "deployment_target_type_id", "op":"eq", "val": "emr"}]'),
           q=False)
dts = SerializableGenerator(results)

for data in dts:
    obj = json.loads(data)
    file(obj)

od = dict(sorted(eks_clusters.items()))

for account, clusters in od.items():
    print(account)
    for cluster in clusters:
        print("\t" + cluster)



