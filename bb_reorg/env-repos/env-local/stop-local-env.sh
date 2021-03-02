#!/bin/bash
# Make sure kubectl is pointing to the minikube environment
ENV_CONTEXT=$(kubectl config current-context)
IS_LOCAL=$(echo "${ENV_CONTEXT}" | grep 'minikube')
if [ -z "${IS_LOCAL}" ]; then
  echo "This command only works for the local minikube environment.  You are currently set to: ${ENV_CONTEXT}"
  exit 1
fi

COMMON_FILES=('nginx-ingress.yaml' 'mongodb.yaml' 'redis.yaml' 'service-gateway.yaml' 'account-manager.yaml' 'authentication-server.yaml' 'watch-configmaps-rbac.yaml')
INPUT_FILES="$@"
KUBE_FILES=("${COMMON_FILES[@]}" "${INPUT_FILES[@]}")

echo "Deleting kube manifests: ${KUBE_FILES[@]}"

for file in ${KUBE_FILES[@]}; do
  echo "Deleting kube manifest: $file"
  kubectl delete --all -f $file
done
