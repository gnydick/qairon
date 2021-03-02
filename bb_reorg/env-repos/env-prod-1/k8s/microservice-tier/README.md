# "microservice" tier

In that directory, we store all k8s manifests and `values.yaml` files for "ego-microservice" Helm chart that used for deploying services on a "microservice" tier.

## Configuring Helm tool

1. Add Artifactory Helm Repository to your Helm Charts.

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories.

     ```$ helm repo update```

## Deploy example of "push-notification-server" by "ego-helm-release/ego-microservice" (EGO service with k8s Secret)

1. Change directory to `microservice-tier` tier directory.

     ```$ cd /home/$USER/env-prod-1/k8s/microservice-tier```

2. Check active "kubectl" cluster.

     ```$ kubectl config current-context```

3. Deploy "push-notification-server" to EKS cluster. In Pipelines we will pull secret from "Vault" and pass them to "--set".

     ```$ helm install ego-helm-release/ego-microservice -f ./push-notification-server-values.yaml --namespace=default --name-template=push-notification-server --set secret.secretContents.PRIVATE_KEY_ID=iur3eeKiroque,secret.secretContents.PRIVATE_KEY=Chieghiv9hodi```

4. Check that "push-notification-server" deployed successfully.

     ```$ helm ls -n default && kubectl get po -l app=push-notification-server -n default```

## Deploy example of "content-manager" by "ego-helm-release/ego-microservice" (EGO service with or without k8s ServiceAccount)

1. Change directory to `microservice-tier` tier directory.

     ```$ cd /home/$USER/env-prod-1/k8s/microservice-tier```

2. Check active "kubectl" cluster.

     ```$ kubectl config current-context```

3. Deploy "content-manager" to EKS cluster.

     ```$ helm install ego-helm-release/ego-microservice -f ./content-manager-values.yaml --namespace=default --name-template=content-manager```

4. Check that "content-manager" deployed successfully.

     ```$ helm ls -n default && kubectl get po -l app=content-manager -n default && kubectl get serviceaccounts -l app=content-manager -n default```

## Deploy example of "authoritative-game-server" by "ego-helm-release/authoritative-game-server"

1. Change directory to `microservice-tier` tier directory.

     ```$ cd /home/$USER/env-prod-1/k8s/microservice-tier```

2. Check active "kubectl" cluster.

     ```$ kubectl config current-context```

3. Deploy "authoritative-game-server" to EKS cluster.

   In Pipelines we will pull secret from "Vault" and pass them to "--set".

   "authoritative-game-server" Helm chart has "split" ("sprig" template functions for Go templates) it will split ".Release.Name" by "-" delimeter and use third value for "EGO_ORGANIZATION_ID".

     ```$ helm install ego-helm-release/authoritative-game-server -f ./authoritative-game-server-values.yaml --namespace=default --name-template=game-server-withme --set secret.secretContents.EGO_ORGANIZATION_PASSWORD=sah9Aephaigha```

4. Check that "authoritative-game-server" deployed successfully.

     ```$ helm ls -n default && kubectl get po -l app=game-server-withme -n default && kubectl get serviceaccounts -l app=game-server-withme -n default```