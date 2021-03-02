#!/bin/bash
KUBE_FILES="$@"
if [ -z "${1}" ]; then
  echo "Missing argument for the Kubernetes yaml file"
  exit 1
fi

MINIKUBE_IP=`minikube ip`
echo '<!DOCTYPE html>'
echo '<html>'
echo '<head>'
echo '  <title>Ego Services Local Environment</title>'
echo '</head>'
echo '<body>'
echo '<h1>Ego Services Local Environment</h1>'
echo '<p>This web page is produced from the gen-index-html.sh script in the env-local repository.  The script needs to '
echo '   be run after each deployment or redeployment because internal ports may have changed or services may have '
echo '   become available or unavailable.  It may also be run to detect new log zip file archives.  After running the'
echo '   script, reload the page.'
echo '</p>'

SERVICE_GATEWAY_PODS=`kubectl get pod -l "component=service-gateway" -o jsonpath='{range .items[*]}{@.metadata.name}{"\n"}{end}'`
for service_gateway_pod in ${SERVICE_GATEWAY_PODS}; do
  echo '<p>Here are the names of the (REST/gRPC) port environment variables for the deployed services:</p>'
  PORT_ENVS=`kubectl exec ${service_gateway_pod} -- env | grep 'GRPC\|REST' | sort`
  echo '<pre>'
  echo "${PORT_ENVS}"
  echo '</pre>'
  break;
done

echo '<p>Here are some commands you may find helpful when interacting with your local cluster:</p>'
echo '<pre>'
echo '  # Re-run the script that produces this HTML page (from the root of the env-local repo)'
echo '  ./gen-index-html.sh local-basic.yaml > out/index.html'
MONGODB_PODS=`kubectl get pods -l "component=mongodb" -o jsonpath='{.items[*].metadata.name}'`
for mongo_pod in "${MONGODB_PODS}"; do
echo
echo '  # Run the mongo shell in the mongo container'
echo "  kubectl exec -it ${mongo_pod} -c mongodb -- mongo"
done
echo
echo '  # Deploy another microservice cluster (after having started with the local-basic.yaml):'
echo '  kubectl apply -f connection-manager.yaml'
echo
echo '  # Shutdown the cluster (started with the local-basic.yaml and the connection-manager.yaml):'
echo '  kubectl delete -f local-basic.yaml -f connection-manager.yaml'
echo '  minikube stop'
echo
echo '  # After the minikube stop, you can remove the VM to start later from a clean slate (when necessary):'
echo '  minikube delete'
echo '</pre>'

#
# MINIKUBE DASHBOARD
#
echo '  <h2>Minikube Dashboard</h2>'
echo '    <p>The Minikube comes with a nice dashboard showing the status of everything in the cluster.  You can also'
echo '       use it to launch (exec) a shell into a running server.  Click on a deployment and then click the Exec'
echo '       button at the top-right of the new window.'
echo '    </p>'
echo '    <ul>'
echo "      <li><a href=\"http://${MINIKUBE_IP}:30000/#!/overview?namespace=default\" target=\"_blank\">Kubernetes Dashboard</a></li>"
echo '    </ul>'

#
# SERVICE GATEWAY DASHBOARD
#
SERVICE_GATEWAY_PORTS=`kubectl get services -l "component=service-gateway" -o jsonpath='{range .items..spec.ports[*]}{@.name}{" "}{@.nodePort}{"\n"}{end}'`
STATUS_PORT=`echo "${SERVICE_GATEWAY_PORTS}" | grep "status" | sed 's/status \([0-9]*\).*/\1/'`
if [ ! -z "${STATUS_PORT}" ]; then
  echo '  <h2>Service Gateway Dashboard</h2>'
  echo '    <p>NGiNX+ comes with a nice dashboard showing some metrics for traffic flowing through the Service Gateway.</p>'
  echo '    <ul>'
  echo "      <li><a href=\"http://${MINIKUBE_IP}:${STATUS_PORT}/dashboard.html\" target=\"_blank\">NGiNX+ Dashboard</a></li>"
  echo '    </ul>'
fi

#
# LOG FILE LINKS
#
echo '  <h2>Log Files</h2>'
declare -a EGO_SERVERS=()
for kubeFile in ${KUBE_FILES}; do
  egoServers=`grep 'image:' ${kubeFile} | grep 'server/' | \
    grep -v 'logmgr-local' | \
    sed 's| *image:.*server/\([^:]*\).*|\1|'`
  for egoServer in ${egoServers}; do
    EGO_SERVERS+=("${egoServer}")
  done
done
LOG_SERVICE_PORTS=`kubectl get services -o jsonpath='{range .items[*]}{@.metadata.name}{"\n"}{range .spec.ports[?(@.name=="logs")]}{@.name}{" "}{@.nodePort}{"\n"}{end}' | grep --no-group-separator -B 1 'logs ' | sed 'N;s/\n/ /' | sed 's/logs //'`
while read -r line; do
  #echo "Service: ${line}"
  LOG_SERVICE_NAME=`echo "${line}" | sed 's/\([^ ]*\).*/\1/'`
  #echo "Service Name: ${LOG_SERVICE_NAME}"
  LOG_SERVICE_PORT=`echo "${line}" | sed 's/[^ ]* \([0-9]*\).*/\1/'`
  if [ ! -z "${LOG_PORT}" ]; then
    continue
  fi
  #echo "Service Port: ${LOG_SERVICE_PORT}"
  COMPONENT_NAME=`kubectl get services -o jsonpath="{range .items[?(@.metadata.name=='${LOG_SERVICE_NAME}')]}{@.spec.selector.component}{'\n'}{end}"`
  #echo "Component Name: ${COMPONENT_NAME}"
  POD_NAME=`kubectl get pods -o jsonpath="{range .items[?(@.metadata.labels.component=='${COMPONENT_NAME}')]}{@.metadata.name}{'\n'}{end}"`
  if [ -z "${POD_NAME}" ]; then
    continue
  fi
  #echo "Pod Name: ${POD_NAME}"
  POD_IP=`kubectl get pod "${POD_NAME}" -o jsonpath='{.status.podIP}'`
  CONTAINERS=`kubectl get pod "${POD_NAME}" -o jsonpath='{range .spec.containers[*]}{@.name}{"\n"}{end}'`
  LOG_CONTAINER=`echo "${CONTAINERS}" | grep "\-logs"`
  if [ ! -z "${LOG_CONTAINER}" ]; then
    SERVER_CONTAINER=`echo "${CONTAINERS}" | grep -v "\-logs"`
    if [ ! -z "${SERVER_CONTAINER}" ]; then
      echo "    <h3>${SERVER_CONTAINER} @ ${POD_IP}</h3>"
      LOG_FILES=`kubectl exec "${POD_NAME}" -c "${SERVER_CONTAINER}" -- ls /opt/withme/logs/`
      echo '      <ul>'
      for log_file in ${LOG_FILES}; do
        LOG_FILE_URL="http://${MINIKUBE_IP}:${LOG_SERVICE_PORT}/${log_file}"
        echo "        <li><a href=\"${LOG_FILE_URL}\" target=\"_blank\" >${log_file}</a></li>"
      done
      echo '      </ul>'
    fi
  fi
  echo
done <<< "${LOG_SERVICE_PORTS}"
echo '</body>'
echo '</html>'

