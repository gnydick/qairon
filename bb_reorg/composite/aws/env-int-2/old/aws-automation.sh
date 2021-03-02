#!/usr/bin/env bash
set -eo pipefail

# Create array with CF templates placed in directory
templateList=($(ls *.yaml))

# Get vault token
VAULT_TOKEN=$(curl --request POST --data "{\"role_id\":\"$EGO_VAULT_ROLE_ID\", \"secret_id\":\"$EGO_VAULT_SECRET_ID\"}" https://vault.withme.com/v1/auth/approle/login | jq .auth.client_token | tr -d '"')

# Get "int-2-rds-cleanspeak" credentials form vault
CS_RDS_MASTER_PASS=$(curl --header "X-Vault-Token:${VAULT_TOKEN}" https://vault.withme.com/v1/cicd/int-2-rds-cleanspeak | jq .data.pass | tr -d '"')

# Function for creating or update AWS resources
aws_create_or_update () {
local templateFile=$1
local stackName=$2
  aws cloudformation deploy  --template-file ./${templateFile} --stack-name ${stackName} --no-fail-on-empty-changeset --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM
}

## Create or update all AWS resources from CF templates
while [ ${#templateList[@]} -gt 0 ]; do
  for template in "${templateList[@]}"; do
    ## Catch Cleanspeak RDS CF Template and pass "MasterUserPassword"
    # Regexp check ${template} variable
    if [[ ${template} == *"rds-cleanspeak"* ]]; then
      aws cloudformation deploy --template-file ./${template} --stack-name $(echo ${template} | cut -f1 -d".") --parameter-overrides MasterUserPassword=${CS_RDS_MASTER_PASS} --no-fail-on-empty-changeset
      #Remove already used an item from an array
      templateList=( ${templateList[@]/${template}/} )
    else
      ## Deploy CF template as usual
      # "cut" remove “.yaml“ from a variable that pass to “--stack-name“
      aws_create_or_update ${template} $(echo ${template} | cut -f1 -d".")
      #Remove already used an item from an array
      templateList=( ${templateList[@]/${template}/} )
    fi
  done
done
