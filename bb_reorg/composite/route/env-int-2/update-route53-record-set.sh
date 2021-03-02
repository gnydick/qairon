#!/bin/bash
#
# Creates or removes a Route53 Alias within a Hosted Zone associated with a subdomain within the
# the withme.com domain (e.g. int-2.withme.com) to an AWS load balancer created from a
# Kubernetes deployment of an ingress or service of type LoadBalancer. The script accepts several
# arguments.
#
# Author: Erik K. Worth

# JSON Template.  See https://docs.aws.amazon.com/cli/latest/reference/route53/change-resource-record-sets.html
read -r -d '' RECORD_SET_CHANGE_JSON_TEMPLATE <<EOF
{
  "ChangeBatch":
  {
    "Changes": [
      {
        "Action": "__ACTION__",
        "ResourceRecordSet": {
          "Name": "__SUBDOMAIN__",
          "Type": "A",
          "AliasTarget": {
            "HostedZoneId": "__HOSTED_ZONE_ID__",
            "DNSName": "__DNS_NAME__",
            "EvaluateTargetHealth": false
          }
        }
      }
    ]
  }
}
EOF

function getRecordSetChangJsonPayload() {
  local _ACTION=$1
  local _SUBDOMAIN=$2
  local _HOSTED_ZONE_ID=$3
  local _DNS_NAME=$4
  local _json=`echo "${RECORD_SET_CHANGE_JSON_TEMPLATE}" | \
    sed "s|__ACTION__|${_ACTION}|g" | \
    sed "s|__SUBDOMAIN__|${_SUBDOMAIN}|g" | \
    sed "s|__HOSTED_ZONE_ID__|${_HOSTED_ZONE_ID}|g" | \
    sed "s|__DNS_NAME__|${_DNS_NAME}|g"`
  echo ${_json}
}

# Print help
function help() {
  echo usage: update-route53-record-set.sh
  echo " -n <arg>"
  echo " --name <arg>         The service name for the load balancer"
  echo
  echo " --namespace <arg>    The namespace for the load balancer (e.g. ingress-nginx)"
  echo
  echo " -s <arg>"
  echo " --subdomain <arg>    The sub-domain for the environment (e.g. int-2.withme.com)"
  echo
  echo " -a <arg"
  echo " --action <arg>        The update action from one of these: {UPSERT | DELETE}"
  echo
  exit 1
}

NAMESPACE="default"
# Parse command line arguments
while [[ $# -gt 1 ]]
do
key="$1"

case ${key} in
    -n|--name)
    SERVICE_NAME="$2"
    shift # past argument
    ;;
    --namespace)
    NAMESPACE="$2"
    shift # past argument
    ;;
    -s|--subdomain)
    SUBDOMAIN="$2"
    shift # past argument
    ;;
    -a|--action)
    ACTION="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift
done

# Validate command line arguments
if [ -z "${SERVICE_NAME}" ]; then
  echo Missing --name argument
  help
fi
if [ -z "${SUBDOMAIN}" ]; then
  echo Missing --subdomain argument
  help
fi
if [ -z "${ACTION}" ]; then
  echo Missing --action argument
  help
fi
case ${ACTION} in
    UPSERT)
    echo "Creating or updating Route53 record for ${SUBDOMAIN}"
    ;;
    DELETE)
    echo "Removing Rout53 record for ${SUBDOMAIN}"
    ;;
    *)
    echo "Invalid action: ${ACTION}"
    help
    ;;
esac
echo

# Get the internal hostname for the load balancer created by Kubernetes Load Balancer
LOAD_BALANCER_HOST=`kubectl get service "${SERVICE_NAME}" --namespace="${NAMESPACE}" -o jsonpath='{.status.loadBalancer.ingress..hostname}'`
if [ -z "${LOAD_BALANCER_HOST}" ]; then
  echo "No NGiNX Ingress Load Balancers registered (yet)."
  exit 1
fi
echo "Load Balancer Host: ${LOAD_BALANCER_HOST}"

# Find the corresponding AWS load balancer entry to get it's hosted zone identifier
AWS_LOAD_BALANCERS=`aws elb describe-load-balancers --output text --query 'LoadBalancerDescriptions[*].{ID:CanonicalHostedZoneNameID,DNSName:DNSName}' | grep "${LOAD_BALANCER_HOST}"`
if [ -z "${AWS_LOAD_BALANCERS}" ]; then
  AWS_LOAD_BALANCERS=`aws elbv2 describe-load-balancers --output text --query 'LoadBalancers[*].{ID:CanonicalHostedZoneId,DNSName:DNSName}' | grep "${LOAD_BALANCER_HOST}"`
  if [ -z "${AWS_LOAD_BALANCERS}" ]; then
    echo "Cannot find AWS Load Balancer record corresponding to the load balancer host: ${LOAD_BALANCER_HOST}"
    exit 1
  fi
fi
LOAD_BALANCER_HOSTED_ZONE=""
for aws_lb in ${AWS_LOAD_BALANCERS}; do
  LOAD_BALANCER_HOSTED_ZONE=`echo "${aws_lb}" | sed "s/${LOAD_BALANCER_HOST}\t\(.*\)/\1/"`
done
if [ -z "${LOAD_BALANCER_HOSTED_ZONE}" ]; thenint-1
  echo "Cannot extract load balancer hosted zone from: ${LOAD_BALANCERS}"
  exit 1
fi
echo "Load Balancer Hosted Zone: ${LOAD_BALANCER_HOSTED_ZONE}"

# Get the hosted zone identifier for the Route53 hosted zone for the sub-domain
ROUTE53_HOSTED_ZONES=`aws route53 list-hosted-zones --output text --query 'HostedZones[*].{ID:Id,Name:Name}' | sed 's|.hostedzone/\([^\t]*\)\t\(.*\)|\1 \2|'`
if [ -z "${ROUTE53_HOSTED_ZONES}" ]; then
  echo "No Route53 Hosted Zone for subdomain ${SUBDOMAIN}"
  exit 1
fi
ROUTE53_HOSTED_ZONE=""
while read -r zone; do
  _zone_name=`echo "${zone}" | sed 's|[^ ]* \([^.]*.withme.com\).*|\1|'`
  if [ "${_zone_name}" == "${SUBDOMAIN}" ]; then
    ROUTE53_HOSTED_ZONE=`echo "${zone}" | sed 's|\([^ ]*\).*|\1|'`
    break
  fi
done <<< ${ROUTE53_HOSTED_ZONES}
echo "Route53 hosted zone for ${SUBDOMAIN}: ${ROUTE53_HOSTED_ZONE}"

# Apply the change
RECORD_SET_CHANGE=$(getRecordSetChangJsonPayload "${ACTION}" "${SUBDOMAIN}" "${LOAD_BALANCER_HOSTED_ZONE}" "${LOAD_BALANCER_HOST}")
echo "Applying Record Set Change to Route53 Hosted Zone ${ROUTE53_HOSTED_ZONE}:"
echo "${RECORD_SET_CHANGE}"

CHANGE_INFO=`aws route53 change-resource-record-sets --output text --hosted-zone-id "${ROUTE53_HOSTED_ZONE}" --cli-input-json "${RECORD_SET_CHANGE}"`
if [ "DELETE" == "${ACTION}" ]; then
  # If we deleted the entry, then we are done
  echo "Route53 Change Info: ${CHANGE_INFO}"
  exit 0
fi

# Wait for the DNS change to propagate
echo "Route53 Change Info: ${CHANGE_INFO}"
CHANGE_ID=`echo "${CHANGE_INFO}" | sed 's|CHANGEINFO.\([^\t ]*\).*|\1|'`
CHANGE_STATUS=`echo "${CHANGE_INFO}" | sed 's|CHANGEINFO.[^\t ]*.\([^\t ]*\).*|\1|'`
echo -n "Awaiting DNS propagation."
while [ "${CHANGE_STATUS}" == "PENDING" ]; do
  echo -n "."
  sleep 5
  CHANGE_STATUS=`aws route53 get-change --id "${CHANGE_ID}" | sed 's|CHANGEINFO.[^\t ]*.\([^\t ]*\).*|\1|'`
done
echo
echo "Change Propagated to AWS Route53 DNS Servers: ${CHANGE_STATUS}"
# TODO: Wait for the IP address to propagate using `dig A ${SUBDOMAIN}`
