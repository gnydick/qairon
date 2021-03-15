#!/bin/bash
#
# Unit tests for command-tag.sh
#
# Author: Erik K. Worth
#

# Make sure the test is run from the root directory for the repo
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
ROOT_PATH=${SCRIPT_PATH%%/scripts/test}
cd ${ROOT_PATH}

# Import the functions to be tested
source ${ROOT_PATH}/scripts/main/command-tag.sh

function assertEquals() {
  local _expected=$1
  local _actual=$2
  if [[ "${_expected}" != "${_actual}" ]]; then
    echo "Expected [${_expected}] != [${_actual}]"
    echo "FAILED"
    exit 1
  fi
}

function testGetSupportedLayerSuccess() {
  local _layer=$1
  echo "---"
  echo "testGetSupportedLayerSuccess: ${_layer}"
  getSupportedLayer "_test_layer" ${_layer}
  assertEquals "${_layer}" "${_test_layer}"
  echo "PASSED"
}

function testGetSupportedLayerFailure() {
  local _layer=$1
  local _error=$2
  echo "---"
  echo "testGetSupportedLayerFailure: ${_layer}"
  local _result=$(getSupportedLayer "_test_layer" ${_layer})
  assertEquals "${_error}" "${_result}"
  echo "PASSED"
}

function testGetSupportedCommandSuccess() {
  local _command=$1
  echo "---"
  echo "testGetSupportedCommandSuccess: ${_command}"
  getSupportedCommand "_test_command" ${_command}
  assertEquals "${_command}" "${_test_command}"
  echo "PASSED"
}

function testGetSupportedCommandFailure() {
  local _command=$1
  local _error=$2
  echo "---"
  echo "testGetSupportedCommandFailure: ${_command}"
  local _result=$(getSupportedCommand "_test_command" ${_command})
  assertEquals "${_error}" "${_result}"
  echo "PASSED"
}

function testGetSupportedRegionSuccess() {
  local _region=$1
  echo "---"
  echo "testGetSupportedRegionSuccess: ${_region}"
  getSupportedRegion "_test_region" ${_region}
  assertEquals "${_region}" "${_test_region}"
  echo "PASSED"
}

function testGetSupportedRegionFailure() {
  local _region=$1
  local _error=$2
  echo "---"
  echo "testGetSupportedRegionFailure: ${_region}"
  local _result=$(getSupportedRegion "_test_region" ${_region})
  assertEquals "${_error}" "${_result}"
  echo "PASSED"
}

function testGetSupportedTierSuccess() {
  local _tier=$1
  echo "---"
  echo "testGetSupportedTierSuccess: ${_tier}"
  getSupportedTier "_test_tier" ${_tier}
  assertEquals "${_tier}" "${_test_tier}"
  echo "PASSED"
}

function testGetSupportedTierFailure() {
  local _tier=$1
  local _error=$2
  echo "---"
  echo "testGetSupportedTierFailure: ${_tier}"
  local _result=$(getSupportedTier "_test_tier" ${_tier})
  assertEquals "${_error}" "${_result}"
  echo "PASSED"
}

function testGetTargetFileSuccess() {
  local _layer=$1
  local _tier=$2
  local _target=$3
  local _expected=$4
  echo "---"
  echo "testGetTargetFileSuccess: ${_layer} ${_tier} ${_target}"
  getTargetFile "_test_path" ${_layer} ${_tier} ${_target}
  assertEquals "${_expected}" "${_test_path}"
  echo "PASSED"
}

function testGetTargetFileFailure() {
  local _layer=$1
  local _tier=$2
  local _target=$3
  local _error=$4
  echo "---"
  echo "testGetTargetFileFailure: ${_layer} ${_tier} ${_target}"
  local _result=$(getTargetFile "_test_path" ${_layer} ${_tier} ${_target})
  assertEquals "${_error}" "${_result}"
  echo "PASSED"
}

function testMakeCommandTagSuccess() {
  local _command=$1
  local _target_file=$2
  local _expected_tag=$3
  echo "---"
  echo "testMakeCommandTagSuccess ${_command} ${_target_file}"
  makeCommandTag "_test_tag" ${_command} ${_target_file}
  assertEquals "${_expected_tag}" "${_test_tag}"
  echo "PASSED"
}

function testMakeCommandFromTagSuccess() {
  local _tag=$1
  local _expected_command=$2
  echo "---"
  echo "testMakeCommandFromTagSuccess: ${_tag}"
  makeCommandFromTag "_test_actual" ${_tag}
  assertEquals "${_expected_command}" "${_test_actual}"
  echo "PASSED"
}

testGetSupportedLayerSuccess k8s
testGetSupportedLayerSuccess aws
testGetSupportedLayerFailure unsupported "getSupportedLayer: layer [unsupported], must be one of: aws|k8s"

testGetSupportedCommandSuccess update
testGetSupportedCommandFailure unsupported "getSupportedCommand: command [unsupported], must be one of: update|create"

testGetSupportedRegionSuccess us-west-2
testGetSupportedRegionFailure unsupported "getSupportedRegion: region [unsupported], must be one of: us-west-2"

testGetSupportedTierSuccess game-server-tier
testGetSupportedTierSuccess microservice-tier
testGetSupportedTierSuccess monitoring-tier
testGetSupportedTierFailure unsupported "getSupportedTier: tier [unsupported], must be one of: game-server-tier|microservice-tier|monitoring-tier|udp-routing"

testGetTargetFileSuccess k8s microservice-tier game-server-manager k8s/microservice-tier/game-server-manager-values.yaml
testGetTargetFileSuccess aws us-west-2/microservice-tier nodes aws/config/us-west-2/microservice-tier/nodes.yaml
testGetTargetFileFailure aws us-west-2/microservice-tier node "getTargetFile: file not found at path [aws/config/us-west-2/microservice-tier/node.yaml]"

testMakeCommandTagSuccess update "k8s/microservice-tier/game-server-manager-values.yaml" update-k8s-microservice-tier-game-server-manager-v00001
testMakeCommandTagSuccess update "aws/config/us-west-2/microservice-tier/nodes.yaml" update-aws-us-west-2-microservice-tier-nodes-v00001
testMakeCommandTagSuccess create "aws/config/us-west-2/game-server-tier/nodes2.yaml" create-aws-us-west-2-game-server-tier-nodes2-v00001

testMakeCommandFromTagSuccess update-k8s-microservice-tier-game-server-manager-v00001 "\
        helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username \$ART_BUILD_USER --password \$ART_BUILD_PASSWORD && \
        helm repo update && \
        helm upgrade game-server-manager ego-helm-release/ego-microservice -f k8s/microservice-tier/game-server-manager-values.yaml --namespace=default --install --reuse-values --atomic --wait --timeout 600s"
testMakeCommandFromTagSuccess update-aws-us-west-2-microservice-tier-nodes-v00001 "cd aws && sceptre update us-west-2/microservice-tier/nodes.yaml --yes"
testMakeCommandFromTagSuccess create-aws-us-west-2-game-server-tier-nodes2-v00001 "cd aws && sceptre create us-west-2/game-server-tier/nodes2.yaml --yes"
