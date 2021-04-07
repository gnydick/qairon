#!/usr/bin/env bash

BASEDIR=$(/bin/pwd)
echo -n '' > init_failures.txt
for MOD in $(find * -type d)
do
    pushd $MOD
    tf12 init
    if [[ "$?" != "0" ]]; then
      echo $MOD >> $BASEDIR/init_failures.txt
    fi
    popd
done