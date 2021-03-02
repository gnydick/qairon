#!/bin/bash
#
# This script will check to see if a container in a Pod is ready after it has been deployed.  Call
# it with three arguments:
# * namespace (e.g. "default")
# * component-name (e.g. "connection-manager")
# * container-name (e.g. "connection-manager" or absent when the same as the component-name)
#
NAMESPACE=$1
COMPONENT_NAME=$2
CONTAINER_NAME=$3
if [ -z "${CONTAINER_NAME}" ]; then
  CONTAINER_NAME=${COMPONENT_NAME}
fi
POD_NAME=`kubectl get pods --namespace="${NAMESPACE}" -o jsonpath="{range .items[?(@.metadata.labels.app=='${COMPONENT_NAME}')]}{@.metadata.name}{'\n'}{end}"`
if [ -z "${POD_NAME}" ]; then
  POD_NAME=`kubectl get pods --namespace="${NAMESPACE}" -o jsonpath="{range .items[?(@.metadata.labels.component=='${COMPONENT_NAME}')]}{@.metadata.name}{'\n'}{end}"`
  if [ -z "${POD_NAME}" ]; then
    echo "No component with name ${COMPONENT_NAME}"
    exit 1
  fi
fi
CMD="kubectl get pod ${POD_NAME} --namespace=${NAMESPACE} -o jsonpath='{range .status.containerStatuses[?(@.name==\"${CONTAINER_NAME}\")]}{@.ready}'"
#echo "CMD: ${CMD}"
POD_READY=`eval "${CMD}"`

if [ "true" != "${POD_READY}" ]; then
  echo "POD_READY=${POD_READY}"
fi
while [ "true" != "${POD_READY}" ]; do
  sleep 1
  echo -n '.'
  POD_READY=`eval "${CMD}"`
done
echo "Pod ${POD_NAME} ready"

