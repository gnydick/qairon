#!/bin/bash

CFG_AREA=$1
ENV=$2
NEW_DIR="$1/$2"

if [[ -d "$NEW_DIR" ]]; then
  echo "Directory already exists: $NEW_DIR"
  exit 255
else
  rsync -var $CFG_AREA/.skel/ $NEW_DIR/
fi