# etcd-operator Helm value file for chart "ego-helm-release/etcd-operator"

In that directory we store `values.yaml` file for "etcd-operator" Helm chart that used for deploy ETCD on "database" tier nodes.

* [ Custom values.yaml file for "etcd-operator" ]( https://bitbucket.org/imvu/env-prod-1/src/master/k8s/database-tier/etcd-operator/etcd-operator-values.yaml )

## Deploy "etcd-operator"

1. Add Artifactory Helm Repository to your Helm Charts

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Change directory to database tier directory

     ```$ cd /home/$USER/env-prod-1/k8s/database-tier/etcd-operator```

4. Check active "kubectl" cluster

     ```$ kubectl config current-context```

5. Deploy "etcd-operator" to EKS cluster

     ```$ helm install -f ./etcd-operator-values.yaml --namespace=database --name-template=etcd-operator ego-helm-release/etcd-operator```

6. Check that etcd pods running without issues

     ```$ kubectl get po -n database```

7. Check that all etcd pod is "Running"

     ```$ kubectl get po -n database```

## Update already deployed "etcd-operator"

1. Check already deployed Helm charts to namespace

     ```bash
          $ helm ls --namespace=database
          NAME         	NAMESPACE	REVISION	UPDATED                                	STATUS  	CHART               	APP VERSION
          etcd-operator	database 	3       	2019-12-27 15:20:24.939751687 +0200 EET	deployed	etcd-operator-0.10.2	0.9.4  
     ```

2. Update chart list from Helm Repositories. Increasing "etcdCluster.size" from `3` to `5`

     ```$ helm upgrade etcd-operator ego-helm-release/etcd-operator -f ./etcd-operator-values.yaml --set etcdCluster.size=5 --namespace=database```