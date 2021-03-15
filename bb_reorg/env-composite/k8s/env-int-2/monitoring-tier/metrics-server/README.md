# KUBERNETES METRICS-SERVER

Directory with Kubernetes Metrics Server k8s manifests.

"Kubernetes Metrics Server" must be treated as simple metrics server that collecting the simplest metrics in EKS cluster.
It helps with showing simple metrics in "kubectl" commands and that will be helpful for a fast downgrade to more detailed metrics in Prometheus/Grafana.
"Kubernetes Metrics Server" needed for normal work of [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

## Deploy Kubernetes Metrics Server

1. Change directory to root Sceptre Project directory

    ```$ cd /home/$USER/env-int-2/monitoring```

2. Check your active `kubectl` cluster:

    ```$ kubectl config current-context```

3. Deploy `Kubernetes Metrics Server`:

    ```$ kubectl apply -f ./metrics-server/```

4. Check `Kubernetes Metrics Server`:

    ```$ kubectl get deployment metrics-server -n kube-system```

## Kubernetes Metrics Server features

1. Check your nodes resource consumption:

    ```$ kubectl top nodes```

    ```$ kubectl top node ${NODE_NAME}```

2. Check your podes resource consumption:

    ```$ kubectl top pod -n ${NAMESPACE_NAME}```
