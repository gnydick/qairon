# Monitoring tools and Helm values files for charts

In that directory we store all k8s manifests and `values.yaml` files for Helm charts that used for deploy cluster monitoring components.

## Directory guide

Directory guide :

* [Custom values.yaml file for "Prometheus-Operator"]( https://bitbucket.org/imvu/env-cicd/src/master/monitoring/prometheus-operator/prometheus-operator-values.yaml )

* [Custom Grafana Dashboards in k8s ConfigMap file]( https://bitbucket.org/imvu/env-cicd/src/master/monitoring/prometheus-operator/grafana-dashboards )

* [Default k8s metrics-server]( https://bitbucket.org/imvu/env-cicd/src/master/monitoring/metrics-server )

## Deploy Prometheus-Operator

1. Add Artifactory Helm Repository to your Helm Charts

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Change directory to monitoring tier directory

     ```$ cd /home/$USER/env-cicd/monitoring/prometheus-operator```

4. Check active "kubectl" cluster

     ```$ kubectl config current-context```

5. Deploy "Prometheus-Operator" to EKS cluster

     ```$ helm install prom-operator ego-helm-release/prometheus-operator -f ./prometheus-operator-values.yaml --set grafana.adminPassword=$GRAF_PASS --namespace=monitoring```

6. Check that Prometheus pods running without issues

     ```$ kubectl get po -n monitoring```

7. Check that all Prometheus "Targets" is "UP"

     ```$ kubectl -n monitoring port-forward svc/prometheus-operated 9090:9090```

   Open link in your web browser:

     ```http://localhost:9090/targets```

8. Check that Grafana view metrics from Prometheus.

     ```$ kubectl -n monitoring port-forward svc/prom-operator-grafana 8080:80```

   Open link in your web browser:

     ```http://localhost:8080```

## Update Prometheus-Operator

1. Add Artifactory Helm Repository to your Helm Charts

     ```$ helm repo add ego-helm-release https://withme.jfrog.io/withme/ego-helm-release/ --username $ARTIFACTORY_USERNAME --password $ARTIFACTORY_PASSWORD```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Set Grafana "admin" password in environment variable

     ```$ export GRAF_PASS=$YOUR_SECRET_PASSWORD```

     ```$ export API_KEY=$OPSGENIE_API_KEY```

4. Change directory to monitoring tier directory

     ```$ cd /home/$USER/env-cicd/monitoring/prometheus-operator```

5. Check active "kubectl" cluster

     ```$ kubectl config current-context```

6. Check that helm "Prometheus-Operator" deployment exist

     ```$ helm ls -n monitoring```

7.  Update "Prometheus-Operator" in EKS cluster

    ```helm upgrade --install --namespace=monitoring \
    -f ./kube-prometheus-stack-values.yaml \
    prom-stack ego-helm-release/kube-prometheus-stack \
    --set grafana.adminPassword=$GRAF_PASS \
    --set alertmanager.config.global.opsgenie_api_key=$API_KEY \
    --set alertmanager.config.receivers[1].webhook_configs[0].http_config.basic_auth.password=$HEARBEAT_API_KEY
    ```

    Secrets `$GRAF_PASS` can be found in Vault `cicd/prometheus-operator_env-cicd`

## Deploy/update Custom Grafana Dashboard

1. Check active "kubectl" cluster.

     ```$ kubectl config current-context```

2. Change directory to "grafana-dashboards" directory.

     ```$ cd /home/$USER/env-cicd/monitoring/prometheus-operator/grafana-dashboards```

3. Apply k8s ConfigMap to create or update "Custom Grafana Dashboard".

     ```$ kubectl apply -f ./<DASHBOARD_FILE_NAME>.yaml```
