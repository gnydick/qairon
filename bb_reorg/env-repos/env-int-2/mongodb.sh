#!/bin/bash
#
# Opens a mongo shell for the MongoDB database.  Run the command without arguments to see the
# supported arguments.
#
# Author: Erik K. Worth
#
ENV_CONTEXT=$(kubectl config current-context)
IS_INT_2=$(echo "${ENV_CONTEXT}" | grep 'int-2')
if [ -z "${IS_INT_2}" ]; then
  echo "This command only works for the int-2 environment.  You are currently set to: ${ENV_CONTEXT}"
  exit 1
fi

# MongoDB command to get the status of the replica set.  This will tell which instance is primary.
RS_STATUS_COMMAND_FILE="/tmp/get-replica-set-status.js"
cat >${RS_STATUS_COMMAND_FILE} <<EOF
rs.status();
EOF

# Print help
function help() {
  echo usage: suspend_account
  echo " -f <arg>"
  echo " --file <arg>         The file with the mongo commands to run"
  echo
  exit 1
}

FILE=""
# Parse command line arguments
while [[ $# -gt 1 ]]
do
key="$1"

case $key in
    -f|--file)
    FILE="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift
done

DATABASE_SECRET_USER="mongors-auth"
DATABASE_SECRET_USERNAME=$(kubectl get secret --namespace database ${DATABASE_SECRET_USER} -o jsonpath="{.data.username}" | base64 --decode)
DATABASE_SECRET_PASSWORD=$(kubectl get secret --namespace database ${DATABASE_SECRET_USER} -o jsonpath="{.data.password}" | base64 --decode)

# Check replica 0 to see which replica is primary
DATABASE="mongors-0"
RS_STATUS_JSON=$(kubectl -it exec ${DATABASE} --namespace database -- mongo --username ${DATABASE_SECRET_USERNAME} --password ${DATABASE_SECRET_PASSWORD} < ${RS_STATUS_COMMAND_FILE} 2>/dev/null)
PRIMARY_REPLICA_NUMB=$(echo "JSON: ${RS_STATUS_JSON}" | grep -B 10 '"stateStr" : "PRIMARY"' | grep '_id' | sed 's|.*"_id" : \([0-9]*\).*|\1|')
if [ -z "${PRIMARY_REPLICA_NUMB}" ]; then
  echo "Unable to establish the primary replica for the mongoDB replica set in int-2"
  exit 1
fi
PRIMARY_REPLICA="mongors-${PRIMARY_REPLICA_NUMB}"
if [ -z "${FILE}" ]; then
  kubectl -it exec ${PRIMARY_REPLICA} --namespace database -- mongo --username ${DATABASE_SECRET_USERNAME} --password ${DATABASE_SECRET_PASSWORD}
else
  kubectl -it exec ${PRIMARY_REPLICA} --namespace database -- mongo --username ${DATABASE_SECRET_USERNAME} --password ${DATABASE_SECRET_PASSWORD} < ${FILE} 2>/dev/null
fi
