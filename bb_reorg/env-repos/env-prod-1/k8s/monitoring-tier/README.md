# Monitoring tier manifests and Helm values files for charts

In that directory we store all k8s manifests and `values.yaml` files for Helm charts that used for deploy cluster components on "monitoring" tier nodes.

## Directory guide

Directory guide :

* [Custom values.yaml file for "Prometheus-Stack"]( https://bitbucket.org/imvu/env-prod-1/src/master/k8s/monitoring-tier/kube-prometheus-stack-values.yaml )

* [Custom Grafana Dashboards in k8s ConfigMap file]( https://bitbucket.org/imvu/env-prod-1/src/master/k8s/monitoring-tier/grafana-dashboards )

## Deploy/Update Prometheus-Stack

1. Add Artifactory Helm Repository to your Helm Charts

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Set Grafana "admin" password in environment variable

     ```export GRAF_PASS=$YOUR_SECRET_PASSWORD && \
        export API_KEY=$OPSGENIE_API_KEY && \
        export HEARBEAT_API_KEY=$HEARBEAT_API_KEY
     ```

4. Change directory to monitoring tier directory

     ```$ cd env-prod-1/k8s/monitoring-tier ```

5. Check active "kubectl" cluster

     ```$ kubectl config current-context```

6. Deploy/Upgrade "Prometheus-Stack" to EKS cluster

     ```helm upgrade --install --namespace=monitoring \
     -f ./kube-prometheus-stack-values.yaml \
     prom-stack ego-helm-release/kube-prometheus-stack \
     --set grafana.adminPassword=$GRAF_PASS \
     --set alertmanager.config.global.opsgenie_api_key=$API_KEY \
     --set alertmanager.config.receivers[1].webhook_configs[0].http_config.basic_auth.password=$HEARBEAT_API_KEY
     ```

     Secrets `$GRAF_PASS` `$HEARBEAT_API_KEY` and `$API_KEY` can be found in Vault `cicd/prod-1/prometheus-operator`

7. Check that Prometheus pods running without issues

     ```$ kubectl get po -n monitoring```

8. Check that all Prometheus "Targets" is "UP"

     ```$ kubectl -n monitoring port-forward svc/prometheus-operated 9090:9090```

   Open link in your web browser:

     ```http://localhost:9090/targets```

9. Check that Grafana view metrics from Prometheus.

      ```https://grafana-ui.withme.com/```

   Open link in your web browser:

     ```http://localhost:8080```

## Deploy New Relic Agent (nri-bundle)

1. Add Artifactory Helm Repository to your Helm Charts

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Change directory to monitoring tier directory

     ```$ cd env-prod-1/k8s/monitoring-tier ```

4. Set New Relic "LICENSE_KEY" in environment variable

     ```export LICENSE_KEY=$NEW_RELIC_LICENSE_KEY```

5. Check active "kubectl" cluster

     ```$ kubectl config current-context```

6. Deploy "newrelic-bundle" to EKS cluster

```sh
helm install newrelic-bundle ego-helm-release/nri-bundle -f ./new-relic-nri-values.yaml -n newrelic \
--set global.licenseKey=$LICENSE_KEY \
--set global.cluster=prod-1 
```

## Upgrade New Relic Agent (nri-bundle)

1. Add Artifactory Helm Repository to your Helm Charts

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Change directory to monitoring tier directory

     ```$ cd env-prod-1/k8s/monitoring-tier ```

4. Upgrade "newrelic-bundle" Helm release in cluster

```sh
helm upgrade newrelic-bundle ego-helm-release/nri-bundle -f new-relic-nri-values.yaml -n newrelic --reuse-values
```
