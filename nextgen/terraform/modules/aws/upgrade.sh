#!/usr/bin/env bash

BASEDIR=$(/bin/pwd)
INIT_FAILURES=$BASEDIR/init_failures.txt
echo -n '' > $BASEDIR/upgrade_failures.txt

for MOD in $(find * -type d  | grep -v .terraform | grep -vxf init_failures.txt)
do
    pushd $MOD
    tf13 0.13upgrade -yes
    if [[ "$?" != "0" ]]; then
      echo $MOD >> $BASEDIR/upgrade_failures.txt
    fi
    popd
done