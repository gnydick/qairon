# Directory guide

Directory guide :

* [Custom values.yaml file for "Prometheus-Stack"]( https://bitbucket.org/imvu/env-int-2/src/master/monitoring/kube-prometheus-stack-values.yaml )

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

     ```$ cd /home/$USER/env-int-2/monitoring```

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

     Secrets `$GRAF_PASS` can be found in Vault `cicd/int-2/prometheus-operator`

7. Check that Prometheus pods running without issues

     ```$ kubectl get po -n monitoring```

8. Check that all Prometheus "Targets" is "UP"

     ```$ kubectl -n monitoring port-forward svc/prometheus-operated 9090:9090```

   Open link in your web browser:

     ```http://localhost:9090/targets```

9. Check that Grafana view metrics from Prometheus.

     ```$ kubectl -n monitoring port-forward svc/prom-stack-grafana 8080:80```

   Open link in your web browser:

     ```http://localhost:8080```

## Deploy DataDog Agent

1. Add Helm Repository to your Helm

     ```$ helm repo add datadog https://helm.datadoghq.com.```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Change directory to monitoring tier directory

     ```$ cd env-int-2/k8s/monitoring-tier ```

4. Set DataDog "API_KEY" in environment variable

     ```export DD_API_KEY=$DATADOG_API_KEY```

5. Check active "kubectl" cluster

     ```$ kubectl config current-context```

6. Deploy "datadog-agent" to EKS cluster

```sh
helm install datadog-agent datadog/datadog -n datadog -f datadog-agent-values.yaml --set datadog.site='datadoghq.com' --set datadog.apiKey=$DD_API_KEY 
```

## Upgrade DataDog Agent

1. Update chart list from Helm Repositories

     ```$ helm repo update```

2. Change directory to monitoring tier directory

     ```$ cd env-int-2/k8s/monitoring-tier ```

3. Upgrade "datadog-agent" Helm release in cluster

```sh
helm upgrade datadog-agent datadog/datadog -n datadog -f datadog-agent-values.yaml --reuse-values
```