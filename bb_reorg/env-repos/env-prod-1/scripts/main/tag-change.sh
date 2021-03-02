#!/bin/bash
#
# Create a properly formatted tag for a configuration change to the state of the operatioal system.
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
  echo "usage: tag-change <command> <template-file>"
  echo "  where <command> is one of: ${_SUPPORTED_COMMANDS}"
  echo "  and <template-file> is a file below one of these directories: ${_SUPPORTED_LAYERS}"
  echo
  exit 1
}

if [[ $# -lt 2 ]]; then
  echo "Missing arguments."
  help
fi
if [[ $# -gt 2 ]]; then
  echo "Warning extra arguments. Only two are used."
fi

COMMAND=$1
TARGET_FILE=$2
if [[ ! -f "${TARGET_FILE}" ]]; then
  echo "File not found at path [${TARGET_FILE}].  If relative path, then make it relative to [${ROOT_PATH}]"
  help
fi

# Produce the tag string from the command and the file
makeCommandTag "TAG" ${COMMAND} ${TARGET_FILE}

echo "Tag Name: ${TAG}"
git tag -a ${TAG} -m "Tag command ${COMMAND} for the file ${TARGET_FILE}"
