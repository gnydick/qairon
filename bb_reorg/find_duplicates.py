import os
from pathlib import Path
from os import path

import sys
import yaml
from cfn_tools import load_yaml, dump_yaml


def load_dirs(dir):
    p = Path(dir)
    return [x for x in p.iterdir() if x.is_dir()]


def register_envr_content(envr, content):
    if content not in contents:
        contents[content] = list()
    contents[content].append(envr)


def get_files(p, extensions):
    files = list()
    results = [x for x in p.iterdir() if not x.is_dir() and x.suffix in extensions]
    files.extend(results)
    for x in p.iterdir():
        if x.is_dir():
            deep_results = get_files(x, extensions)
            files.extend(deep_results)
    return files


contents = dict()
base_dir = sys.argv[1]
repos = load_dirs(base_dir)

for repo in repos:
    content_dirs = load_dirs(repo)

    for d in content_dirs:
        register_envr_content(repo.name, d.name)

with open("possible_duplicates.txt", 'w') as dupes:
    for content, envrs in contents.items():
        if len(envrs) > 1:
            dupes.write("%s: %s\n" % (content, ", ".join([x for x in envrs])))

# compare contents to see if they're duplicates
checksums = dict()
p = Path(base_dir)

config_files = dict()


def register_config_file(config_file):
    paths = [x for x in config_file.parts[2:]]
    # paths.append(config_file.name)
    uniq_file = os.sep.join(paths)
    if uniq_file not in config_files:
        config_files[uniq_file] = list()


    config_files[uniq_file].append(config_file.parts[1])
    pass


for content, envrs in contents.items():
    checksums[content] = dict()
    for envr in envrs:
        dir = p.joinpath(envr)
        files = get_files(dir, ['.json', '.yaml', '.yml'])
        for config_file in files:
            register_config_file(config_file)
            print(config_file)


pass
