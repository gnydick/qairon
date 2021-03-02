# KUBERNETES DASHBOARD

Directory with kubernetes Dashboard k8s manifests.

## Deploy Kubernetes Dashboard

1. Change directory to root Sceptre Project directory

    ```$ cd /home/$USER/env-prod-1/k8s/util-tier/dashboard```

2. Check your active `kubectl` cluster:

    ```$ kubectl config current-context```

3. Deploy `Kubernetes Dashboard`:

    ```$ kubectl apply -f ./kubernetes-dashboard.yaml -f ./eks-admin-service-account.yaml```

## Access Kubernetes Dashboard

1. Check your active `kubectl` cluster:

    ```$ kubectl config current-context```

2. Get access Token

    ```$ kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | awk '/^deployment-controller-token-/{print $1}') | awk '$1=="token:"{print $2}'```

3. Start kubectl proxy:

    ```$ kubectl proxy```

4. Open that link and login by Token.

    ```http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#!/login```