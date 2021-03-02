# Configuring cluster and deploy helm tiller to it

* Elements
     * About NginX Ingress Controller
     * Deployment Nginx Ingress Controller by Helm with 'values-nginx.yaml'
     * Helm values-nginx.yaml
     * Ingress rule example

## About NginX Ingress Controller

* NginX Ingress controller parts:
     1. AWS ELB (ELB with SSL Termination)
     2. Ingress controller K8s Service
     3. Ingress controller K8s Pod
     4. K8s Ingress rules

For our start purposes in "cicd" cluster is better to use NginX Ingress Controller L7.
We using NginX Ingress Controller L7 with SSL termination on AWS ELB side.

## Deployment NginX Ingress Conroller by Helm with 'values-nginx.yaml'

### Helm values-nginx.yaml

Certificate will be attached to ingress controller by certificate ARN
In `values-nginx.yaml` you can find line with:
```YAML
service.beta.kubernetes.io/aws-load-balancer-ssl-cert: arn:aws:acm:us-west-2:407733091588:certificate/f8854997-8ae4-420c-87ab-968e0cf4e55a
```

For enabling getting real remoteIP from AWS ELB:
```YAML
use-proxy-protocol: "true"
```
```YAML
use-proxy-protocol: "true"
service.beta.kubernetes.io/aws-load-balancer-proxy-protocol: '*'
```

Default Ingress Controller image:
```YAML
repository: 407733091588.dkr.ecr.us-west-2.amazonaws.com/ego-cicd/ingress-controller-nginx
tag: "0.23.0"
```

Default Ingress backend (404-page) image:
```YAML
repository: 407733091588.dkr.ecr.us-west-2.amazonaws.com/ego-cicd/ingress-controller-nginx
tag: "backend"
```

Check your Helm system variables:
```bash
echo $HELM_HOME
echo $HELM_TLS_CA_CERT
echo $HELM_TLS_CERT
echo $HELM_TLS_ENABLE
echo $HELM_TLS_KEY
```
Every echo command must have output.
Described in [ helm-initiation ](https://bitbucket.org/imvu/env-cicd/src/master/helm-initiation/README.md) part.

Installation with prepared `values-nginx.yaml`:

```bash
helm install stable/nginx-ingress --name nginx-ingress -f ./values-nginx.yaml --namespace ingress
```

After Helm install command we can check Ingress K8s pod/deployments and K8s service by command:
```bash
kubectl get all --namespace ingress
```

By values in `values-nginx.yaml` you must have:
     * 2 Controller K8s pod
     * 1 Backend K8s pod
     * 1 Ingress controller K8s service
     * 1 Backend K8s service

For checking readiness of NginX:
```bash
kubectl get svc --namespace ingress
```
When service will get external address you can follow it from your browser and get default backend-404 page.

## Ingress rule examples

K8s Ingress rule for exposing service to Internet thru NginX Ingress Controller:
```YAML
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  namespace: jenkins
  name: jenkins-ingress
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
    - host: jenkins.withme.com
      http:
        paths:
          - backend:
              serviceName: jenkins
              servicePort: 8080
            path: /
```

## Deployment NginX Ingress Conroller for proxy pass UI's to DUO DAG by Helm with 'values-nginx.yaml'

Here we will use the main benefit of using Helm Charts.
All that we needed just run Helm install command with a different name.

```bash
helm install stable/nginx-ingress --name nginx-ingress-duo -f ./values-nginx.yaml --namespace ingress
```
Now we have second Ingress controller for all UI's and "proxy pass" them to DUO without any unexpected effect on Jenkins. 
