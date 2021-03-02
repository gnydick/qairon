# KubeDB Operator

Here you can find kubernetes manifests that used for deploy KubeDB Operator and databases.

Content:

- KubeDB Operator
- KubeDB Operator catalogs

## Deploy KubeDB Operator 0.12.0 with Helm 3

1. Create namespace "database": `kubectl create namespace database`
2. Switch your kubectl config default namespace: `kubectl config set-context --current --namespace=database`
3. Change directory to: `./env-int-2/kubedb`
4. Add 'appscode' helm repo `helm3 repo add appscode https://charts.appscode.com/stable/ && helm3 repo update`
5. Install "kubedb-operator" by Helm with using custom variables: `helm3 install --namespace=database --name-template=kubedb-operator -f ./values.yaml appscode/kubedb --version 0.12.0`
   [Detail info about KubeDB Operator install](https://kubedb.com/docs/0.12.0/setup/install/)
6. Check that all CRD are ready (in output must have 16 CRD's): `kubectl get crd -l app=kubedb | grep 'kubedb' | wc -l`
7. Apply "kubedb-catalog" directory recursively: `kubectl apply -f ./kubedb-catalog --recursive`
8. Check that KubeDB operator is running normally: `kubectl get po -l app=kubedb -n database`

## Update KubeDB Operator with Helm 3

1. Change directory to: `./env-int-2/kubedb`
2. Make changes in `values.yaml`
3. Upgrade release by Helm: `helm3 upgrade --namespace database -f ./values.yaml kubedb-operator  appscode/kubedb --version 0.12.0`
4. Check upgrade status: `helm3 history kubedb-operator`

## KubeDB CheatSheet

- Check "MongoDB" Objects: `kubectl get mg`
- Check snapshots: `kubectl get snap`
- Describe "MongoDB" Object: `kubectl describe mg ${mongodb_object_name}`

## Who you can contact about it

- mklipikov@imvu.com
