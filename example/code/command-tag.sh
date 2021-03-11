#!/bin/bash
#
# Specifies functions used to create and parse tags used to represent commands according to a
# naming convention.
#
# Author: Erik K. Worth
#

# For the proper work on MacOS install GNU sed: brew install gnu-sed
# and make a symlink: sudo ln -s /usr/local/bin/gsed /usr/local/bin/sed

# The supported virtualization layers. AWS is the cloud-provider and Kubernetes
# a virtualization layer on top of the cloud-provider
_SUPPORTED_LAYERS="aws|k8s"

# The supported commands in this command abstraction.  These commands will map to real commands but
# logically makes sense.
_SUPPORTED_COMMANDS="update|create"

# The regions within the hosted environment supported by this utility
_SUPPORTED_REGIONS="us-west-2"

# The same as the above, but formatted so it can be used in a regular expression to select a region
_SUPPORTED_REGIONS_ESC=$(echo ${_SUPPORTED_REGIONS} | sed "s:[|]:\\\|:g")

# The "tiers" of computing resources supported by this utility
_SUPPORTED_TIERS="game-server-tier|microservice-tier|monitoring-tier|udp-routing"

# Thesame as the above, but formatted so it can be used in a regular expression to select a tier
_SUPPORTED_TIERS_ESC=$(echo ${_SUPPORTED_TIERS} | sed "s:[|]:\\\|:g")

# The key that identifies the automate operation version
_VERSION_KEY="controlVersion"

#
# Get the virtualization layer argument from those that are supported and set it into the variable
# with the name provided in the first argument. This reports an error and exits if the layer is
# not supported.
#
# $1: result_var: the name of a variable to hold the name of the layer produced by this function
# $2: layer: the provided virtualization layer to be validated and set in the result
#
# Example:
# getSupportedLayer "_target_layer" "aws"
# echo "${_target_layer}"
# aws
function getSupportedLayer() {
  if [[ -z "$1" ]]; then
    echo "getSupportedLayer: Missing result variable name as first argument"
    exit 1
  else
    local _result_var=$1
  fi
  if [[ "${2}" =~ $(echo ^\(${_SUPPORTED_LAYERS}\)$) ]]; then
    local _layer=${2}
  else
    echo "getSupportedLayer: layer [${2}], must be one of: ${_SUPPORTED_LAYERS}"
    exit 1
  fi
  eval $_result_var="'${_layer}'"
}

#
# Get the command argument from those that are supported and set it into the variable
# with the name provided in the first argument. This reports an error and exits if the command is
# not supported.
#
# $1: result_var: the name of a variable to hold the name of the command produced by this function
# $2: command: the provided command to be validated and set in the result
#
# Example:
# getSupportedCommand "_target_command" "update"
# echo "${_target_command}"
# update
function getSupportedCommand() {
  if [[ -z "$1" ]]; then
    echo "getSupportedCommand: Missing result variable name as first argument"
    exit 1
  else
    local _result_var=$1
  fi
  if [[ "${2}" =~ $(echo ^\(${_SUPPORTED_COMMANDS}\)$) ]]; then
    local _command=${2}
  else
    echo "getSupportedCommand: command [${2}], must be one of: ${_SUPPORTED_COMMANDS}"
    exit 1
  fi
  eval $_result_var="'${_command}'"
}

#
# Get the region argument from those that are supported and set it into the variable
# with the name provided in the first argument. This reports an error and exits if the region is
# not supported.
#
# $1: result_var: the name of a variable to hold the name of the region produced by this function
# $2: region: the provided region to be validated and set in the result
#
# Example:
# getSupportedRegion "_target_region" "us-west-2"
# echo "${_target_region}"
# update
function getSupportedRegion() {
  if [[ -z "$1" ]]; then
    echo "getSupportedRegion: Missing result variable name as first argument"
    exit 1
  else
    local _result_var=$1
  fi
  if [[ "${2}" =~ $(echo ^\(${_SUPPORTED_REGIONS}\)$) ]]; then
    local _region=${2}
  else
    echo "getSupportedRegion: region [${2}], must be one of: ${_SUPPORTED_REGIONS}"
    exit 1
  fi
  eval $_result_var="'${_region}'"
}

#
# Get the tier argument from those that are supported and set it into the variable
# with the name provided in the first argument. This reports an error and exits if the tier is
# not supported.
#
# $1: result_var: the name of a variable to hold the name of the tier produced by this function
# $2: tier: the provided tier to be validated and set in the result
#
# Example:
# getSupportedTier "_target_tier" "microservices-tier"
# echo "${_target_tier}"
# microservices-tier
function getSupportedTier() {
  if [[ -z "$1" ]]; then
    echo "getSupportedTier: Missing result variable name as first argument"
    exit 1
  else
    local _result_var=$1
  fi
  if [[ "${2}" =~ $(echo ^\(${_SUPPORTED_TIERS}\)$) ]]; then
    local _tier=${2}
  else
    echo "getSupportedTier: tier [${2}], must be one of: ${_SUPPORTED_TIERS}"
    exit 1
  fi
  eval $_result_var="'${_tier}'"
}

#
# Get the path from the repo root to the target file based on the layer and target
#
# $1 result_var: the name of a variable to hold the name of the tag produced by this function
# $2 layer: the virtualization layer for the command from one of these values: "aws" or "k8s"
# $3 tier: the tier in which the target resides
# $4 target: the target of the command
#
# Example:
# getTargetFile "path" k8s microservice-tier game-server-manager
# echo "${path}"
# k8s/microservice-tier/game-server-manager-values.yaml
function getTargetFile() {
  if [[ -z "$1" ]]; then
    echo "getTargetFile: Missing result variable name as first argument"
    exit 1
  else
    local _result_var=$1
  fi
  getSupportedLayer "_target_file_layer" ${2}
  if [[ "${_target_file_layer}" == "aws" ]]; then
    getSupportedRegion "_target_file_region" "${3%%/*}"
  fi
  getSupportedTier "_target_file_tier" ${3##*/}
  if [[ "${_target_file_layer}" == "aws" ]]; then
    local _target="aws/config/${_target_file_region}/${_target_file_tier}/${4}.yaml"
  else
    local _target="k8s/${_target_file_tier}/${4}-values.yaml"
  fi
  if [[ ! -f "${_target}" ]]; then
    echo "getTargetFile: file not found at path [${_target}]"
  fi
  eval $_result_var="'${_target}'"
}

#
# Create a git tag based on a command and a file with changes
#
# $1 result_var: the name of a variable to hold the name of the tag produced by this function
# $2 command: the supported command to run
# $3 target_file: the path to the file with the changes in it
#
# Example:
# makeCommandTag tag update k8s/microservice-tier/game-server-manager-values.yaml
# echo "${tag}"
# update-k8s-microservice-tier-game-server-manager-v00001
function makeCommandTag() {
  if [[ -z "$1" ]]; then
    echo "makeCommandTag: Missing result variable name as first argument"
    exit 1
  else
    local _result_var=$1
  fi
  getSupportedCommand "_make_tag_command" ${2}
  local _target_file=$3
  if [[ ! -f "${_target_file}" ]]; then
    echo "makeCommandTag: File not found [${_target_file}]. Make sure your working directory is the repo root."
    exit 1;
  fi

  # Extract the layer from the first path in the file
  getSupportedLayer "_make_tag_layer" ${_target_file%%/*}
  local _parsed=${_make_tag_layer}

  if [[ "${_make_tag_layer}" == "aws" ]]; then
    # When this is a change at the AWS layer, extract the region from the next path segment
    getSupportedRegion "_make_tag_region" $(echo ${_target_file} | sed "s#${_parsed}/config/\(${_SUPPORTED_REGIONS_ESC}\).*#\1#")
    _parsed="${_parsed}/config/${_make_tag_region}"
  fi

  # Extract the tier from the first path in the file
  getSupportedTier "_make_tag_tier" $(echo ${_target_file} | sed "s#${_parsed}/\([^/]*\)/.*#\1#")
  _parsed="${_parsed}/${_make_tag_tier}"

  # Extract the target
  if [[ "${_make_tag_layer}" == "aws" ]]; then
    local _target=$(echo ${_target_file} | sed "s#${_parsed}/\(.*\).yaml#\1#")
  else
    local _target=$(echo ${_target_file} | sed "s#${_parsed}/\(.*\)-values.yaml#\1#")
  fi

  local _version=$(grep "${_VERSION_KEY}" ${_target_file} | tr -d '[:space:]' | sed "s#^\#${_VERSION_KEY}:\([0-9]*\)\$#\1#")
  if [[ -z "${_version}" ]]; then
    echo -e "Control version in the updated file does not exist or not in numeric format. Please add the string to the file:\n# ${_VERSION_KEY}: 1"
    exit 1
  else
    _version=$(printf "%05d" ${_version})
  fi

  # Format the tag
  if [[ "${_make_tag_layer}" == "aws" ]]; then
    local _tag_name="${_make_tag_command}-${_make_tag_layer}-${_make_tag_region}-${_make_tag_tier}-${_target}-v${_version}"
  else
    local _tag_name="${_make_tag_command}-${_make_tag_layer}-${_make_tag_tier}-${_target}-v${_version}"
  fi

  # Make sure the tag name is legal
  git check-ref-format "tags/${_tag_name}" || { echo "makeCommandTag: Invalid tag name [${_tag_name}]"; exit 1; }

  eval $_result_var="'${_tag_name}'"
}

#
# Function for checking that microservice is using secrets and fetch them from Vault.
#
function checkVaultSecrets() {
  # Check passed arguments to function
  if [[ -z "$1" ]]; then
    echo "checkVaultSecrets: Missing microservice values file path as first argument"
    exit 1
  else
    local _target_file=$1
  fi
  if [[ -z "$2" ]]; then
    echo "checkVaultSecrets: Missing microservice name as second argument"
    exit 1
  else
    local _target_name=$2
  fi
  # Check that microservice needs secret. If ".secret.create == false" then whole function will be skipped.
  _secretTrue=$(yq .secret.create < "${_target_file}")
  if [[ "$_secretTrue" != "true" ]]; then
    return
  fi
  # Validate variables with Vault credentials
  if [[ -z "$EGO_VAULT_ROLE_ID" ]]; then
    echo "Variable \$EGO_VAULT_ROLE_ID has to be defined."
    exit 1
  fi
  if [[ -z "$EGO_VAULT_SECRET_ID" ]]; then
    echo "Variable \$EGO_VAULT_SECRET_ID has to be defined."
    exit 1
  fi
  # Make Vault login
  vault_token=$(vault write -address="https://vault.withme.com/" -format=json auth/approle/login role_id="${EGO_VAULT_ROLE_ID}" secret_id="${EGO_VAULT_SECRET_ID}" | jq .auth.client_token | sed -e 's/^"//' -e 's/"$//')
  vault login -no-print="true" -address="https://vault.withme.com/" token="${vault_token}"
  # Check that microservice has secrets in vault. 
  # Whole pipeline will be failed if microservice ".secret.create == true" but missing secrets in Vault.
  if [[ -z $(vault list cicd/prod-1/base64 | grep "${_target_name}") ]]; then
    echo "checkVaultSecrets: The secret for ${_target_name} must be placed in Vault!"
    exit 1
 fi
  # Extracting secrets from Vault and format them for passing to Helm install/update command.
  _vaultSecrets=$(vault kv get -address="https://vault.withme.com/" -format=json cicd/prod-1/base64/"${_target_name}" | jq -r '.data | to_entries | .[] | .key + "=" + .value' | sed "s/^/--set-string secret.secretContents./g" | xargs)
  echo "${_vaultSecrets}"
}

#
# Creates a sceptre or helm command string from a tag
#
# $1: result_var: the name of a variable to hold the resulting command string
# $2: tag: the git tag
function makeCommandFromTag() {
  if [[ -z "$1" ]]; then
    echo "makeCommandFromTag: Missing result variable name as first argument"
    exit 1
  else
    local _result_var=$1
  fi
  if [[ -z "$2" ]]; then
    echo "makeCommandFromTag: Missing tag as second argument"
    exit 1
  else
    local _tag_name=${2}
  fi

  # Extract the command from the tag
  getSupportedCommand "_make_command_command" $(echo "${_tag_name}" | sed 's#\([^-]*\).*#\1#')
  local _parsed="${_make_command_command}"

  # Extract the virtualization layer from the tag
  getSupportedLayer "_make_command_layer" $(echo "${_tag_name}" | sed "s#${_parsed}-\([^-]*\).*#\1#")
  _parsed="${_parsed}-${_make_command_layer}"

  if [[ "${_make_command_layer}" == "aws" ]]; then
    # When this is a change at the AWS layer, extract the region from the tag
    getSupportedRegion "_make_command_region" $(echo "${_tag_name}" | sed "s#${_parsed}-\(${_SUPPORTED_REGIONS_ESC}\).*#\1#")
    _parsed="${_parsed}-${_make_command_region}"
  fi

  # Extract the tier from the tag
  getSupportedTier "_make_command_tier" $(echo "${_tag_name}" | sed "s#${_parsed}-\(${_SUPPORTED_TIERS_ESC}\).*#\1#")
  _parsed="${_parsed}-${_make_command_tier}"
  local _target=$(echo "${_tag_name}" | sed "s#${_parsed}-\(.*\)-v[0-9]*#\1#")

  # Produce the appropriate command
  if [[ "${_make_command_layer}" == "aws" ]]; then
    getTargetFile "_make_command_target_file" ${_make_command_layer} "${_make_command_region}/${_make_command_tier}" ${_target}
    _make_command_target_file=$(echo "${_make_command_target_file}" | sed "s#aws/config/##")
    local _command_string="cd aws && sceptre ${_make_command_command} ${_make_command_target_file##/*} --yes"
  else
    getTargetFile "_make_command_target_file" ${_make_command_layer} ${_make_command_tier} ${_target}
    # Checking on using secrets and passing them to variable "_vaultSecrets" if they are exist
    getVaultSecrets=$(checkVaultSecrets "${_make_command_target_file}" "${_target}")
    local _command_string="\
        helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username \$ART_BUILD_USER --password \$ART_BUILD_PASSWORD && \
        helm repo update && \
        helm upgrade ${_target} ego-helm-release/ego-microservice -f ${_make_command_target_file} ${getVaultSecrets} --namespace=default --install --atomic --wait --timeout 600s"
  fi

  eval $_result_var="'${_command_string}'"
}
