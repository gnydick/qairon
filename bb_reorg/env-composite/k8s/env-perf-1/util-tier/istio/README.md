# Istio

Here you can find istio manifests and Helm configuration for installation and configuration of VirtualServices and Gateways.

## Source

Istio-init and istio-cp were cloned from the official GitHub Repository: <https://github.com/istio/istio/tree/1.3.8/install/kubernetes/helm/>

## Difference

### Istio-init

1. value.yaml:
    * hub: 407733091588.dkr.ecr.us-west-2.amazonaws.com/ego-cicd/istio - Changed to use AWS ECR instead of Istio registry
    * tag: 1.3.8 - To install specific (latest at this point) version of Istio

### Istio-cp

1. value.yaml:
    * hub: 407733091588.dkr.ecr.us-west-2.amazonaws.com/ego-cicd/istio - Changed to use AWS ECR instead of Istio registry
    * tag: 1.3.8 - To install specific (latest at this point on 1.3.x) version of Istio
    * defaultNodeSelector: { prod-1-tier: util } - To set default Affinity rule for Istio resources
2. charts/gateways/templates/daemonset.yaml:
    * New file. To support an option to launch Istio Gateway as a daemon set (needed for service gateway)
3. charts/gateways/values.yaml:
    * externalTrafficPolicy: Local - to preserve source IP
4. charts/pilot/values.yaml:
    * kkeepaliveMaxServerConnectionAge: 2562047h47m16.854775807s

## Istio-init installation

1. Create namespace "istio-system": `kubectl create namespace istio-system`
2. Update Istio-init configuration (value.yaml) to contain URL to ECR and Image tag (if needed)
3. Install Istio-init via Helm: `helm install istio-init ego-helm-release/istio-init --namespace istio-system`
4. Update Istio-cp configuration (value.yaml) to contain URL to ECR, Image tag and other configs(if needed)
5. Install Istio-cp via Helm: `helm install istio-cp .ego-helm-release/istio-cp --namespace istio-system`

* Note: Istio NLB has [issue in AWS](https://github.com/kubernetes/kubernetes/issues/69264) and it fixed only in EKS 1.16.

## Who you can contact about it

* mklipikov@imvu.com
* dkonstantynov@imvu.com
