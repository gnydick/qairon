# MongoDB Exporter

Here you can find Helm `values-mongors.yaml` vith all used values for deploy MongoDB Exporter for "mongors" ReplicaSet.

Content:

- MongoDB Exporter

## Deploy MongoDB Exporter 2.4.0 with Helm 3

### Preconfiguring

1. For getting metrics from MongoDB we will need to create in that MongoDB database User and give him needed "read" role.

Here example of MongoDB Query:

__Note: Change "HERE_YOUR_SECRET_PASSWORD" to the real one.__

```mongo
db.getSiblingDB("admin").createUser({
    user: "mongodb_exporter",
    pwd: "HERE_YOUR_SECRET_PASSWORD",
    roles: [
        { role: "clusterMonitor", db: "admin" },
        { role: "read", db: "local" }
    ]
})
```

That Query will create "mongodb_exporter" user with password and assume "read" role to "local" database.

### Deploy

1. Change directory to: `./env-int-2/monitoring/percona-mongodb-exporter`
2. Update deafult helm repo `helm3 repo update`
3. Install "MongoDB Exporter" by Helm with using custom variables and "--set" flag:

    ```bash
    helm3 install --namespace=database --name-template=mongodb-exporter -f ./values-mongors.yaml stable/prometheus-mongodb-exporter \
    --version 2.4.0 \
    --set 'mongodb.uri=mongodb://mongodb_exporter:HERE_YOUR_SECRET_PASSWORD@mongors-1.mongors-gvr.database.svc.cluster.local\,mongors-2.mongors-gvr.database.svc.cluster.local\,mongors-3.mongors-gvr.database.svc.cluster.local:27017/?replicaSet=rs0'`
    ```

4. Verify MongoDB Exporter is working by running these commands:

    ```bash
    kubectl -n database port-forward service/mongodb-exporter-prometheus-mongodb-exporter 9216
    curl http://127.0.0.1:9216/metrics
    ```

5. Now you can check Prometheus Dashboard: `kubectl -n monitoring port-forward svc/prom-prometheus-operator-prometheus 9090:9090`
   Check MongoDB Exporter in "Targets" and check metrics in "Graph" (Expression is "mongodb_*")
