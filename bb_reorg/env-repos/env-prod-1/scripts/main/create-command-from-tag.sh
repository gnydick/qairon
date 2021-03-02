#!/bin/bash
#
# Create a command to apply to the operational system based on the information encoded in a tag
#
# Author: Erik K. Worth
#

# Make sure the script is run from the root directory for the repo
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ROOT_PATH=${SCRIPT_PATH%%/scripts/main}
cd ${ROOT_PATH}

# Import the functions to be tested
source ${ROOT_PATH}/scripts/main/command-tag.sh

# Print help
function help() {
  echo "usage: create-command-from-tag <tag>"
  echo "  where <tag> is a git tag formatted by the tag-change.sh script"
  echo
  exit 1
}

if [[ $# -lt 1 ]]; then
  echo "Missing arguments."
  help
fi
if [[ $# -gt 1 ]]; then
  echo "Warning extra arguments. Only one is used."
fi

TAG=$1
makeCommandFromTag "COMMAND" ${TAG}

echo "Running the command: ${COMMAND}"
eval ${COMMAND}
