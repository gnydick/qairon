#!/bin/bash
#
# Lists the game servers that are not registered for the "game-server-withme" set of game servers
#
# Author: Erik K. Worth
#
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_CONTEXT=$(kubectl config current-context)
IS_PROD_1=$(echo "${ENV_CONTEXT}" | grep 'prod-1')
if [ -z "${IS_PROD_1}" ]; then
  echo "This command only works for the prod-1 environment.  You are currently set to: ${ENV_CONTEXT}"
  exit 1
fi

# MongoDB command to list the registered game servers from the registry collection in the session database
COMMAND_FILE="/tmp/get-registered-game-servers.js"
cat >${COMMAND_FILE} <<EOF
DBQuery.shellBatchSize = 300
use session
db.registry.find({"organizationId":"withme"},{"gameServerHost":1})
EOF

# Retrieve the sorted list of registered game servers in the registry collection of the session database
GAME_SERVERS_JSON=$(${DIR}/mongodb.sh -c game-server-manager -d session -f ${COMMAND_FILE})
REGISTERED_GAME_SERVERS=$(echo "${GAME_SERVERS_JSON}" | grep 'gameServerHost' | sed 's|.*"gameServerHost" : "\([^"]*\).*|\1|' | sort)
if [ -z "${REGISTERED_GAME_SERVERS}" ]; then
  echo "Unable to retrieve registered game servers from the session database"
  exit 1
fi
#echo "Registered Game Servers: ${REGISTERED_GAME_SERVERS}"

# Retreive the list of deployed game servers
DEPLOYED_GAME_SERVERS=$(kubectl get pods -l 'app in (game-server-withme, game-server2-withme)' | grep 'game-server' | grep 'withme' | sed 's|\(game-server.*-withme-[0-9]*\).*|\1|' | sort)
if [ -z "${DEPLOYED_GAME_SERVERS}" ]; then
  echo "Unable to retrieve deployed game servers"
  exit 1
fi
#echo "Deployed Game Servers: ${DEPLOYED_GAME_SERVERS}"
NOT_REGISTERED=$(comm -13 <(echo "${REGISTERED_GAME_SERVERS}") <(echo "${DEPLOYED_GAME_SERVERS}"))
if [ -z "${NOT_REGISTERED}" ]; then
  echo "All game servers appear to be registered"
  exit 0
fi
echo "These game servers are not registered:"
echo "${NOT_REGISTERED}"

