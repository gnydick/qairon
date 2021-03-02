#!/bin/bash
INGRESS_NAME='service-gateway-ingress'
INGRESS_IP=`kubectl -n default get ingress ${INGRESS_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'`
COUNTER=0
while [[ "${COUNTER}" -lt 12 ]]; do
  INGRESS_IP=`kubectl -n default get ingress ${INGRESS_NAME} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'`
  if [[ -z "${INGRESS_IP}" ]]; then
    echo "Waiting for the ingress to become available."
    COUNTER=$(( COUNTER + 1))
    sleep 10s
  else
    echo "The cluster is available now at ${INGRESS_IP}."
    exit 0
  fi
done
if [[ -n "${INGRESS_IP}" ]]; then
  continue
else
  exit 1
fi
