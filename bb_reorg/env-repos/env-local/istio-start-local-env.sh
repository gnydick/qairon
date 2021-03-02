#!/bin/bash
#
# This script was used to try out the Istio service mesh in the local (minikube) environment.  It
# turned out to be heavy and unreliable for a development environment where developers are constantly
# deploying and undeploying services.  It is kept here as a resource because we will probably use it
# for staging and production (and perhaps int-2).
#
# Author: Erik K. Worth
#
KUBE_FILES="$@"
if [ -z "$1" ]; then
  echo "Missing argument local environment configuration file (e.g. local-basic.yaml)"
  exit 1
fi
for kubeFile in ${KUBE_FILES}; do
  if [ ! -f "${kubeFile}" ]; then
    echo "${kubeFile} file not found!"
    exit 1
  fi
done

function getMinikubeState() {
  local _status=${1}
  echo ${_status} | sed "s/minikube: \([^ ]*\).*/\1/"
}

function getClusterState() {
  local _status=${1}
  echo ${_status} | sed 's/.*cluster: \([^ ]*\).*/\1/'
}

function getKubectlState() {
  local _status=${1}
  echo ${_status} | sed 's/.*kubectl: \(.*\)/\1/'
}

function loginToAmazonContainerRepository() {
  eval $(aws ecr get-login --no-include-email --region us-west-2) 2> /dev/null
}

# Make sure the AWS CLI is installed
AWS_CLI=`which aws`
if [ -z "${AWS_CLI}" ]; then
  echo "Install the AWS CLI from here: https://aws.amazon.com/cli/"
  exit 1
fi
echo "aws version:"
aws --version
echo

# make sure istioctl is installed
ISTIOCTL=`which istioctl`
if [ -z "${ISTIOCTL}" ]; then
  echo "Install istioctl"
  exit 1
fi
echo "istioctl version:"
istioctl version
echo

# Make sure the virtualbox VM Driver is installed
VIRTUALBOX=`which virtualbox`
if [ -z "${VIRTUALBOX}" ]; then
  echo "Install Oracle's Virtualbox VM from here: https://www.virtualbox.org/wiki/Downloads"
  exit 1
fi
echo "virtualbox version: `VBoxManage --version`"
echo

# Make sure the Minikube is installed
MINIKUBE=`which minikube`
if [ -z "${MINIKUBE}" ]; then
  echo "Install Minikube from here: https://kubernetes.io/docs/tasks/tools/install-minikube/"
  exit 1
fi
minikube version
echo

# Get the status of the Minikube cluster and VM and start them if they are not Running
MINIKUBE_STATUS=`minikube status`
MINIKUBE_STATE=$(getMinikubeState "${MINIKUBE_STATUS}")
CLUSTER_STATE=$(getClusterState "${MINIKUBE_STATUS}")
KUBECTL_STATE=$(getKubectlState "${MINIKUBE_STATUS}")
MINIKUBE_START_CMD='minikube start --memory=8192 --cpus=4 --kubernetes-version=v1.10.0 --vm-driver=virtualbox'
if [ "${MINIKUBE_STATE}" != "Running" ]; then
  eval $MINIKUBE_START_CMD || { echo 'minikube failed to start' ; exit 1; }
  MINIKUBE_STATUS=`minikube status`
  MINIKUBE_STATE=$(getMinikubeState "${MINIKUBE_STATUS}")
  CLUSTER_STATE=$(getClusterState "${MINIKUBE_STATUS}")
  KUBECTL_STATE=$(getKubectlState "${MINIKUBE_STATUS}")
fi
if [ "${MINIKUBE_STATE}" != "Running" ]; then
  echo 'minikube failed to start'
  exit 1
fi
if [ "${CLUSTER_STATE}" != "Running" ]; then
  echo 'cluster failed to start'
  exit 1
fi

# Make sure Kubectl is installed
KUBECTL=`which kubectl`
if [ -z "${KUBECTL}" ]; then
  echo "Install Kubectl from here: https://kubernetes.io/docs/tasks/tools/install-kubectl/"
  exit 1
fi
echo "kubectl version:"
kubectl version
echo

MINIKUBE_IP=`minikube ip`
if [ "${KUBECTL_STATE}" != "Correctly Configured: pointing to minikube-vm at ${MINIKUBE_IP}" ]; then
  kubectl config use-context minikube || { echo 'Cannot switch kubectl to minikube context' ; exit 1; }
fi
echo "The local cluster is up and running"
echo

# Make sure Docker is installed
DOCKER=`which docker`
if [ -z "${DOCKER}" ]; then
  echo "Install Docker from here: https://docs.docker.com/install/"
  exit 1
fi
echo "docker version:"
docker version
echo

#echo "Enabling the ingress add-on"
#minikube addons enable ingress || { echo 'minikube failed to enable ingress' ; exit 1; }
#echo

echo "Switching to use the minikube's built-in Docker daemon"
eval $(minikube docker-env)
echo

echo "Login to the Amazon Container Repository..."
LOGIN_STATUS=$(loginToAmazonContainerRepository)
echo "${LOGIN_STATUS}"
if [ "${LOGIN_STATUS}" != "Login Succeeded" ]; then
  echo 'Failed to login to the Amazon Container Repository.  Make sure you have an account in the Developer group.'
  exit 1
fi
echo

for kubeFile in ${KUBE_FILES}; do
  # Pull images from Amazon referenced by the kubeFile into the Minikube docker registry
  echo "Pulling Amazon images referenced from ${kubeFile}"
  IMAGES=`grep 'image' ${kubeFile} | grep "amazonaws.com/ego-server" | sed 's/.*image: //'`
  for image in ${IMAGES}; do
    docker pull ${image} || { echo "Error pulling image ${image}" ; exit 1; }
  done
done
echo

# Update /etc/hosts file with a service-gateway entry for the Minikube IP address
ETC_HOSTS='/etc/hosts'
EXISTING_ENTRY=`grep 'service-gateway' ${ETC_HOSTS}`
if [ ! -z "${EXISTING_ENTRY}" ]; then
  EXISTING_IP=`echo "${EXISTING_ENTRY}" | sed 's/\([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\).*/\1/'`
  if [ "${EXISTING_IP}" != "${MINIKUBE_IP}" ]; then
    echo "Updating existing /etc/hosts entry for service-gateway from ${EXISTING_IP} to ${MINIKUBE_IP}"
    sudo sed -i -e "s/${EXISTING_IP}/${MINIKUBE_IP}/g" ${ETC_HOSTS}
  else
    echo "Your /etc/hosts file already has this entry for the Minikube IP: ${EXISTING_ENTRY}"
  fi
else
  echo "Adding entry to /etc/hosts: ${MINIKUBE_IP}   service-gateway"
  sudo echo "${MINIKUBE_IP}   service-gateway" >> ${ETC_HOSTS}
fi

# Support Istio side-cars
ISTIO_INJECTION_ENABLED=`kubectl get namespace default -o jsonpath='{.metadata.labels.istio-injection}'`
if [ "enabled" != "${ISTIO_INJECTION_ENABLED}" ]; then
  kubectl label namespace default istio-injection=enabled
fi

# Wait for kubernetes to become available
./wait-for-pod-ready.sh kube-system kube-scheduler

# Load the Istio service mesh
ISTIO_DIR=$(dirname $(dirname ${ISTIOCTL}))
pushd ${ISTIO_DIR} &> /dev/null || { echo 'changing the working directory to the istio installation' ; exit 1; }
ISTIO_CUSTOM_DEFS_LOADED=`kubectl get crd virtualservices.networking.istio.io -o wide | grep virtualservices.networking.istio.io`
if [ -z "${ISTIO_CUSTOM_DEFS_LOADED}" ]; then
  kubectl apply -f install/kubernetes/helm/istio/templates/crds.yaml
  sleep 10
fi
ISTIO_SERVICES_LOADED=`kubectl get svc --namespace=istio-system istio-ingressgateway | grep istio-ingressgateway`
if [ -z "${ISTIO_CUSTOM_DEFS_LOADED}" ]; then
  kubectl apply -f install/kubernetes/istio-demo.yaml
  sleep 10
  ./wait-for-pod-ready.sh istio-system istio-ingressgateway istio-proxy
fi
popd &> /dev/null

echo "Removing any existing cluster"
for kubeFile in ${KUBE_FILES}; do
  kubectl delete -f ${kubeFile} &> /dev/null
done

echo "Deploying into cluster..."
for kubeFile in ${KUBE_FILES}; do
  kubectl apply -f ${kubeFile} || { echo 'Error deploying into the cluster' ; exit 1; }
done
echo

echo "Deployed."
#./wait-for-ingress.sh

mkdir -p out
echo "Generating Service Environment page in ./out/index.html."
./gen-index-html.sh ${KUBE_FILES} > out/index.html
echo "Opening web page..."
python -mwebbrowser ./out/index.html
