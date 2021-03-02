#!/bin/bash
#
# Opens a mongo shell for the specified database.  Run the command without arguments to see the
# supported arguments.
#
# Author: Erik K. Worth
#
ENV_CONTEXT=$(kubectl config current-context)
IS_PROD_1=$(echo "${ENV_CONTEXT}" | grep 'prod-1')
if [ -z "${IS_PROD_1}" ]; then
  echo "This command only works for the prod-1 environment.  You are currently set to: ${ENV_CONTEXT}"
  exit 1
fi

# Print help
function help() {
  echo usage: suspend_account
  echo " -c <arg>"
  echo " --cluster <arg>      The database cluster name in the Atlas Service"
  echo
  echo " -d <arg>"
  echo " --database <arg>     The name of the database"
  echo
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
    -c|--cluster)
    CLUSTER_NAME="$2"
    shift # past argument
    ;;
    -d|--database)
    DATABASE_NAME="$2"
    shift # past argument
    ;;
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

# Validate command line arguments
if [ -z "${CLUSTER_NAME}" ]; then
  echo Missing --cluster argument
  help
fi
echo

# Validate command line arguments
if [ -z "${DATABASE_NAME}" ]; then
  echo Missing --database argument
  help
fi
echo

echo "Connecting to database '${DATABASE_NAME}'"
DATABASE_SECRET_USER="${DATABASE_NAME}-mongo-auth"
DATABASE_SECRET_USERNAME=$(kubectl get secret ${DATABASE_SECRET_USER} -o jsonpath="{.data.username}" | base64 --decode)
DATABASE_SECRET_PASSWORD=$(kubectl get secret ${DATABASE_SECRET_USER} -o jsonpath="{.data.password}" | base64 --decode)
if [ -z "${FILE}" ]; then
  mongo "mongodb+srv://${CLUSTER_NAME}.nnq5y.mongodb.net/${DATABASE_NAME}" --username ${DATABASE_SECRET_USERNAME} --password ${DATABASE_SECRET_PASSWORD}
else
  mongo "mongodb+srv://${CLUSTER_NAME}.nnq5y.mongodb.net/${DATABASE_NAME}" --username ${DATABASE_SECRET_USERNAME} --password ${DATABASE_SECRET_PASSWORD} < ${FILE} 2>/dev/null
fi

