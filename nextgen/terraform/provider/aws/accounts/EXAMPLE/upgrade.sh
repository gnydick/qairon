#!/usr/bin/env bash

BASEDIR=$(/bin/pwd)
echo -n '' > $BASEDIR/upgrade_failures.txt

for FILE in $(find -type f -name main.tf)
do
    MOD=$(dirname $FILE)
    pushd $MOD
    tf13 0.13upgrade -yes
    if [[ "$?" != "0" ]]; then
      echo $MOD >> $BASEDIR/upgrade_failures.txt
    fi
    popd
done