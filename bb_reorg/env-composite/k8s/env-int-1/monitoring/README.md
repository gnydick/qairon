# Directory guide

Directory guide :

* [DataDog values.yaml file for "DataDog Agent"]( https://bitbucket.org/imvu/env-int-1/src/master/k8s/monitoring/datadog-agent-values.yaml )


## Deploy DataDog Agent

1. Add Helm Repository to your Helm

     ```$ helm repo add datadog https://helm.datadoghq.com.```

2. Update chart list from Helm Repositories

     ```$ helm repo update```

3. Change directory to monitoring tier directory

     ```$ cd env-int-1/k8s/monitoring-tier ```

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

     ```$ cd env-int-1/k8s/monitoring-tier ```

3. Upgrade "datadog-agent" Helm release in cluster

```sh
helm upgrade datadog-agent datadog/datadog -n datadog -f datadog-agent-values.yaml --reuse-values
```
