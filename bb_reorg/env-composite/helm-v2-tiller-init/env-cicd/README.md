# Configuring cluster and deploy helm tiller to it

* Elements
     * Helm parts.
     * RBAC restrictions.
     * Securing Helm tiller with SSL/TLS.
     * Init Helm Tiller in a cluster.
     * Configuring client for using SSL/TLS connection to tiller.
     * Helm implementation plan in "devenv"

## Helm parts

* Helm parts:
     1. Binary Helm client on your workstation (client)
     2. Tiller pod and service in cluster (server)
     3. Helm charts (in repository or locally)

Tiller runs inside of your Kubernetes cluster and manages releases (installations) of your charts.
Helm is a powerful thing for managing applications in a k8s cluster and it can be compared to "apt" package manager for Debian based systems.

## RBAC restrictions

Tiller will be deployed in `default` k8s Namespace and will have the right to deploy in 2 k8s Namespaces `jenkins` and `ingress`.
For managing restricts for tiller we using `tiller-rbac.yaml`
At first we need to check what k8s Namespaces we have:
```bash
kubectl get namespaces
```
If you need to create the new one k8s Namespace for some application that you want to keep from others you can do it by one command:
```bash
kubectl create namespace ${NAMESPACE_NAME}
```

For restricting tiller for some k8s Namespace or vice versa we need edit `tiller-rbac.yaml` and aplly it:
```bash
kubectl apply -f tiller-rbac.yaml
```

## Securing Helm tiller with SSL/TLS

I'm walkthrough [ Generating Certificate Authorities and Certificates ](https://helm.sh/docs/using_helm/#using-ssl-between-helm-and-tiller) and generate all needed certs.

I sign each of CSRs with the CA certificate with the days parameter 3650 days that equals to 10 years.

Users that want to run Helm commands must have certs in `~/helm-certs` directory:
```
# The Helm client files
ca.cert.pem
helm.cert.pem
helm.key.pem
```

## Init Helm Tiller in a cluster

For deploying tiller to cluster you will need to have installed Helm client on your workstation.

Our Tiller is secured by SSL/TLS, so deploy tiller will be custom too.
```bash
helm init --tiller-tls --tiller-tls-cert ./tiller.cert.pem --tiller-tls-key ./tiller.key.pem --tiller-tls-verify --tls-ca-cert ca.cert.pem --service-account tiller --tiller-namespace default
```

## Configuring client for using SSL/TLS connection to tiller.

Helm soon will be added to [ ego-cicd-devenv ](https://bitbucket.org/imvu/ego-cicd-devenv/src/master/)

Right now you can install Helm client by [ tutorial ](https://helm.sh/docs/using_helm/#installing-the-helm-client)

Users that want to run Helm commands must have certs in `~/helm-certs` directory:
```
# The Helm client files
ca.cert.pem
helm.cert.pem
helm.key.pem
```
Certificates can be placed at AWS S3 Bucket and downloaded to developer workstation by AWS CLI command or it's can be part of [ ego-cicd-devenv ](https://bitbucket.org/imvu/ego-cicd-devenv/src/master/) initiation.

For shorting Helm commands we can use environment variables with a path to that certificates and default '--tiller-namespace'.
```bash
export HELM_TLS_CA_CERT=~/helm-certs/ca.cert.pem
export HELM_TLS_CERT=~/helm-certs/helm.cert.pem
export HELM_TLS_KEY=~/helm-certs/helm.key.pem
export HELM_TLS_ENABLE=true
export TILLER_NAMESPACE=default
```
Also, you can add them to `.bashrc` at your user home directory.
And that variables will be exported to the environment at OS startup.

Now you can test your Helm client connection to Tiller:
```bash
helm version
```
If you do configuring steps right you will get output similar to:
```bash
Client: &version.Version{SemVer:"v2.13.0", GitCommit:"79d07943b03aea2b76c12644b4b54733bc5958d6", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.13.0", GitCommit:"79d07943b03aea2b76c12644b4b54733bc5958d6", GitTreeState:"clean"}
```
If Helm client will not have rights to connect Tiller you will get only client version of Helm.

## Helm implementation plan in "devenv"

Helm home directory can be stored in `/home/max/.ego/ego_server/linux-ubuntu-18/x86_64/stuff/helm`
Helm binary can be stored in `/home/max/.ego/ego_server/linux-ubuntu-18/x86_64/stuff/helm/bin`
Helm client certs can be stored in `/home/max/.ego/ego_server/linux-ubuntu-18/x86_64/stuff/helm`

And we need set system variables for "devenv"
```bash
export HELM_HOME=~/.ego/ego_server/linux-ubuntu-18/x86_64/stuff/helm
export HELM_TLS_CA_CERT=~/.ego/ego_server/linux-ubuntu-18/x86_64/stuff/helm/ca.cert.pem
export HELM_TLS_CERT=~/.ego/ego_server/linux-ubuntu-18/x86_64/stuff/helm/helm.cert.pem
export HELM_TLS_KEY=~/.ego/ego_server/linux-ubuntu-18/x86_64/stuff/helm/helm.key.pem
export HELM_TLS_ENABLE=true
export TILLER_NAMESPACE=default
```
With that system variables Helm users will be able to write shorter helm commands without setting all security keys for helm commands.
