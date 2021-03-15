# "service-gateway" tier

In that directory we store all k8s manifests and `values.yaml` files for Helm charts that used for deploy cluster components.

## Directory guide

Directory guide :

* [Custom values.yaml file for "service-gateway" Helm chart]( https://bitbucket.org/imvu/env-perf-1/src/master/k8s/service-gateway-tier/service-gateway-values.yaml )

## "service-gateway" EGO service (based on NginxPlus) for internal trafic routing

## Deploy/upgrade "service-gateway"

1. Add Artifactory Helm Repository to your Helm Charts

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Change directory to `service-gateway-tier` tier directory

     ```$ cd /home/$USER/env-perf-1/k8s/service-gateway-tier```

4. Check active "kubectl" cluster

     ```$ kubectl config current-context```

5. Update "service-gateway" Helm values file if needed. `/home/$USER/env-perf-1/k8s/service-gateway-tier/service-gateway-values.yaml`

6. Deploy/upgrade "service-gateway" to EKS cluster

     ```$ helm upgrade service-gateway ego-helm-release/ego-microservice -f ./service-gateway-values.yaml --namespace=default --install --atomic --wait --timeout 300s```

7. Check that "service-gateway" pods running.

     ```$ kubectl get po -l app=service-gateway -n default```

     ```$ kubectl get ds -n default```


## "duo-nginx-ingress" it's k8s ingress controller for exposing all dasboards that will need DUO athentication

### Deploy "duo-nginx-ingress"

1. Add offical Helm Repository to your Helm Charts

    ```$ helm repo add stable https://kubernetes-charts.storage.googleapis.com/```

2. Update chart list from Helm Repositories

    ```$ helm repo update```

3. Change directory to `service-gateway-tier` tier directory

    ```$ cd /home/$USER/env-prod-1/k8s/service-gateway-tier```

4. Check active "kubectl" cluster

    ```$ kubectl config current-context```

5. Deploy "service-gateway" to EKS cluster

    ```$ helm install nginx-ingress-duo stable/nginx-ingress -f ./duo-nginx-ingress-values.yaml -n kube-system```

6. Check that "service-gateway" pods running.

    ```$ kubectl get po -l release=nginx-ingress-duo -n kube-system```

    ```$ helm ls -n kube-system```
