from pathlib import Path

import sys


def load_dirs(dir):
    p = Path(dir)
    return [x for x in p.iterdir() if x.is_dir()]


def register_envr_content(envr, content):
    if content not in contents:
        contents[content] = list()
    contents[content].append(envr)


contents = dict()
repos = load_dirs(sys.argv[1])

for repo in repos:
    content_dirs = load_dirs(repo)

    for d in content_dirs:
        register_envr_content(repo.name, d.name)

with open("duplicates.txt", 'w') as dupes:
    for content, envrs in contents.items():
        if len(envrs) > 1:
            dupes.write("%s: %s\n" % (content, ", ".join([x for x in envrs])))

