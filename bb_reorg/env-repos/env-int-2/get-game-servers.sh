#!/bin/bash
COMMAND_FILE="/tmp/get-game-servers.js"
cat >${COMMAND_FILE} <<EOF
rs.slaveOk()
use session
db.registry.find({"assignmentState" : "ASSIGNED_TO_SESSION", "organizationId" : "withme"})
EOF
kubectl exec -i --container mongodb mongodb-0 -- mongo < ${COMMAND_FILE}
rm ${COMMAND_FILE}

