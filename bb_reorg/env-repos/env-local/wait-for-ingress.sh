#!/bin/bash
INGRESS_IP=`kubectl get ingress local-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`
if [ -z "${INGRESS_IP}" ]; then
  echo "Waiting for the ingress to become available.  Kill it if it takes more than a minute or two."
fi
while [ -z "${INGRESS_IP}" ]; do
  sleep 1
  echo -n '.'
  INGRESS_IP=`kubectl get ingress local-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`
done
echo
echo "The cluster is available now at ${INGRESS_IP}."
