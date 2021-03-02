#!/bin/bash
COMPONENT_NAME=$1
POD_NAMES=`kubectl get pods -o jsonpath="{range .items[?(@.metadata.labels.component=='${COMPONENT_NAME}')]}{@.metadata.name}{'\n'}{end}"`
if [ -z "${POD_NAMES}" ]; then
  exit
fi
while read -r pod_name; do
  echo "Pod Name: ${pod_name}"
  SERVER_CONTAINER=`kubectl get pod "${pod_name}" -o jsonpath='{range .spec.containers[*]}{@.name}{"\n"}{end}' | grep -v "\-logs"`
  echo "Server Container: ${SERVER_CONTAINER}"
  ERROR=true
  while ${ERROR}; do
    kubectl exec "${pod_name}" -c "${SERVER_CONTAINER}" -- cat /opt/withme/logs/withme-${SERVER_CONTAINER}.log && ERROR=false || { ERROR=true; }
    sleep 1
  done
  echo "====="
done <<< ${POD_NAMES}
