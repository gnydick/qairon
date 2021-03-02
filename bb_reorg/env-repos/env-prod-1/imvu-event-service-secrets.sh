#!/usr/bin/env bash
# NAME: imvu-event-service-secrets
# VERSION: 1.0.0
set -eo pipefail
NAME=$(echo "$BITBUCKET_TAG" | sed 's/\(.*\)-v\([0-9]*\.[0-9]*\.[0-9]*\)$/\1/')
VERSION=$(echo "$BITBUCKET_TAG" | sed 's/\(.*\)-v\([0-9]*\.[0-9]*\.[0-9]*\)$/\2/')

# Get vault token
VAULT_TOKEN=$(curl --request POST --data "{\"role_id\":\"$EGO_VAULT_ROLE_ID\", \"secret_id\":\"$EGO_VAULT_SECRET_ID\"}" https://vault.withme.com/v1/auth/approle/login | jq .auth.client_token | tr -d '"')
echo "Loaded Vault token"
# Get "Imvu Event Service Credentials" form vault
AUTH_TOKEN=$(curl --header "X-Vault-Token:${VAULT_TOKEN}" https://vault.withme.com/v1/cicd/imvu-event-service | jq .data.auth-token | tr -d '"')
CID=$(curl --header "X-Vault-Token:${VAULT_TOKEN}" https://vault.withme.com/v1/cicd/imvu-event-service | jq .data.cid | tr -d '"')

if [ -z "$AUTH_TOKEN" ]; then
  echo "WARNING: IMVU Event Service auth token is missing"
fi

if [ -z "$CID" ]; then
  echo "WARNING: IMVU Event Service cid is missing"
fi

# Base64 encode the secrets
BASE64_AUTH_TOKEN=$(echo -n "${AUTH_TOKEN}" | base64)
BASE64_CID=$(echo -n "${CID}" | base64)

# Configure kubectl for environment
aws eks update-kubeconfig --name prod-1
echo "Switched to prod-1 k8s context"

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: ${NAME}
  labels:
    version: "${VERSION}"
data:
  AUTH_TOKEN: ${BASE64_AUTH_TOKEN}
  CID: ${BASE64_CID}
EOF

echo "Successfully deployed imvu event service secrets. New version: $VERSION"