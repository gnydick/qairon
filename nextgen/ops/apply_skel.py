#!/usr/bin/env python3
import argparse
import os
import shutil
import requests
import json

# in the future, feed this from qairon to autogenerate

parser = argparse.ArgumentParser(description='update from skeleton')
parser.add_argument('dir', type=str,
                    help='directory to updated')
parser.add_argument('level', type=str, help='Options: provider, account, profile, region, target')

args = parser.parse_args()

__levels__ = ['skel', 'provider', 'account', 'profile', 'region']

level = __levels__.index(args.level)

profiles = {
    '407733091588': 'build_user'
}


def process_dir(dir, iter):
    if iter >= len(__levels__):
        return
    source_dir = os.path.sep.join(__levels__[0:iter + 1])
    with os.scandir(dir) as scan_it:
        shutil.copy(os.path.sep.join([source_dir, '.envrc']), dir)
        print(dir)
        for entry in scan_it:
            if entry.is_dir():
                process_dir(entry, iter + 1)


# r = requests.get('http://localhost:5000/api/rest/v1/region')
# data = json.loads(r.text)

# regions = [[r['id'], r['pop']['id']] for r in data['objects']]
# for reg, provider in regions:
#     provider_deets = provider.split(':')
#     reg_paths = reg.split(':')
#     reg_paths.append(reg_paths[2])
#     reg_paths[2] = 'build_user'
#     suffix = os.path.sep.join(reg_paths)
#     dr = os.path.sep.join(['generated', suffix])
#     os.makedirs(dr, exist_ok=True)
#     process_dir(os.path.sep.join(['generated', provider_deets[0]]), level)
process_dir(args.dir, level)

