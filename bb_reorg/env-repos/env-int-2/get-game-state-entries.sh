#!/bin/bash
COMMAND_FILE="/tmp/get-game-state.js"
cat >${COMMAND_FILE} <<EOF
rs.slaveOk()
use gamestate
DBQuery.shellBatchSize = 2500
db.gamestate.find({},{"_id":1,"owner":1,"type":1,"name":1})
EOF
password=$(cat ~/int-2-mongodb-passwd.txt)
kubectl exec -it mongors-0 --namespace database -- mongo --username root --password $password < ${COMMAND_FILE}
rm ${COMMAND_FILE}

