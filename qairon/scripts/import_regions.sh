#!/usr/bin/env bash

DE=$(mktemp /tmp/de.XXXX)
direnv hook bash >$DE
. $DE
rm $DE

for DIR in $@; do
  pop=$(echo $DIR | awk -F "/" '{print $NF}')

  for REG in $(find $DIR -maxdepth 1 -mindepth 1 -type d); do
    region=$(echo $REG | awk -F "/" '{print $NF}')
    echo "REG: $region"
    ./qaironcli region create $provider $region

  done
done
