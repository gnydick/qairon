#!/usr/bin/env bash

DE=$(mktemp /tmp/de.XXXX)
direnv hook bash >$DE
. $DE
rm $DE
for ENV in prod stg dev ; do
  ./qaironcli environment create $ENV
done

./qaironcli pop_type create aws
for FLEET_TYPE in asg nodegroup ; do
  ./qaironcli fleet_type create aws $FLEET_TYPE
done

for REPO_TYPE in ecr nexus ; do
  ./qaironcli repo_type create $REPO_TYPE
done

./qaironcli allocation_type create k8s_mem_gibi Gi
./qaironcli allocation_type create k8s_mem_giga G
./qaironcli allocation_type create k8s_mem_mibi Mi
./qaironcli allocation_type create k8s_mem_mega M
./qaironcli allocation_type create k8s_cpu_milli m

./qaironcli deployment_target_type create eks

for DIR in "$@"; do
  pop=$(echo $DIR | awk -F "/" '{print $NF}')
  ACCT_ID=$(aws sts get-caller-identity | jq -r .Account)
  ./qaironcli pop create aws $provider -n '{"account_id": "'"$ACCT_ID"'"}'
  for REG in $(find $DIR -maxdepth 1 -mindepth 1 -type d); do
    region=$(echo $REG | awk -F "/" '{print $NF}')
    REGION_ID=$(./qaironcli region create $provider $region)
    echo "REG: $region"
    ./qaironcli region create $provider $region

    echo "REGION_ID: $REGION_ID"
    pushd $REG >/dev/null
    _direnv_hook >/dev/null

    aws ec2 describe-availability-zones  | jq -r '.AvailabilityZones[]|[.ZoneName,.ZoneId]|@tsv'  |\
    while read NAME ID ; do
      popd >/dev/null
      ./qaironcli zone create $REGION_ID $NAME -n '{"zone_id": "'"$ID"'"}'
      pushd $REG >/dev/null
    done


    echo "AA_ENV: $AA_ENV"
    echo "VPC_ID=\$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${AA_ENV}-vpc" | jq -r '.Vpcs[].VpcId')"
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=${AA_ENV}-vpc" | jq -r '.Vpcs[].VpcId')
    echo "VPC: $VPC_ID"

    aa=$(echo $AA_ENV | sed 's/prod-//')
    ab=$(echo $aa | sed 's/stage-//')
    ac=$(echo $ab | sed 's/stage/ce/')

    ad=$(echo $ac | sed 's/^dr$/ce-dr/')
    echo "aa: $aa"
    echo "ab: $ab"
    echo "ac: $ac"
    echo "ad: $ad"
    popd
    echo "id=\$(./qaironcli partition create $REGION_ID $ad -n '{\"vpc_id\": \"'\"$VPC_ID\"'\"}')"

    id=$(./qaironcli partition create $REGION_ID $ad -n '{"vpc_id": "'"$VPC_ID"'"}')
    for CIDR in $(aws ec2 describe-vpcs --vpc-id $VPC_ID | jq -r .Vpcs[].CidrBlockAssociationSet[].CidrBlock); do
      echo "./qaironcli network create $id default $CIDR"
      ./qaironcli network create $id default $CIDR
    done

    for EKS in $(aws eks list-clusters | jq -r .clusters[]); do
      ./qaironcli deployment_target create eks $id $ENV $EKS

    done

  done
done
