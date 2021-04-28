#!/usr/bin/env python3
import argparse
import os
import shutil

# in the future, feed this from qairon to autogenerate

parser = argparse.ArgumentParser(description='update from skeleton')
parser.add_argument('dir', type=str,
                    help='directory to updated')
parser.add_argument('level', type=str, help='Options: provider, account, profile, region, target')

args = parser.parse_args()

__levels__ = ['skel', 'provider', 'account', 'profile', 'region', 'target']

level = __levels__.index(args.level)
print(level)


def process_dir(dir, iter):
    source_dir = os.path.sep.join(__levels__[1:level])
    with os.scandir(dir) as scan_it:
        # shutil.copy(os.path.sep.join(source_dir, '.envrc'), dir)
        print(dir)
        for entry in scan_it:
            if entry.is_dir():
                process_dir(entry, iter + 1)

process_dir(args.dir, level)