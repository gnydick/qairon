# Redis

Here you can find values for Redis

## Deploy Redis with Helm

> Pleas note that you will need helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/

1. Change directory to: `./env-int-1/k8s/redis`
2. Install "Redis" by Helm with using custom variables: `helm install -f ./redis-values.yaml ego-helm-release/redis`
3. Check that Redis is running normally(there should be a list of Redis agents equal to the number of nodes, collector and query as configured at values.yaml): `kubectl get po --namespace=observability`

## Update Redis with Helm

1. Change directory to: `./env-int-1/k8s/redis`
2. Make changes in `redis-values.yaml`
3. Upgrade release by Helm: `helm upgrade --namespace observability -f ./redis-values.yaml ego-helm-release/redis`
4. Check upgrade status: `helm3 history redis`

## Who you can contact about it

- alebedintsev@imvu.com
- dkonstantynov@imvu.com
- mklipikov@imvu.com
