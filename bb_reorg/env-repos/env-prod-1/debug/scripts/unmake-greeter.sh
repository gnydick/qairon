#
# Builds the "greeter" username from the provided argument by prepending "[Greeter] " to it and searches for it. 
# If it is found, then it updates the account document for that user to remove the "[Greeter]" prefix from in 
# front of the user's name.
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

USERNAME=$1
if [ -z "${USERNAME}" ]; then
  echo "Missing username argument"
  exit 1
fi
GREETER_USERNAME="[Greeter] ${USERNAME}"

# MongoDB command to list the accounts in the database by the username
QUERY_COMMAND_FILE="/tmp/find-users-by-username.js"
cat >${QUERY_COMMAND_FILE} <<EOF
use account
db.account.find({"profile.username":"${GREETER_USERNAME}"},{"profile.username":1})
EOF

# Retrieve the matching accounts
ACCOUNTS_QUERY_RESULT=$(${DIR}/mongodb.sh -c account-manager -d account -f ${QUERY_COMMAND_FILE})
ACCOUNT_ID=$(echo "${ACCOUNTS_QUERY_RESULT}" | grep "${USERNAME}" | sed 's|.*ObjectId("\([^"]*\)".*|\1|')
#echo "Query Result: ${ACCOUNTS_QUERY_RESULT}"
echo "Account ID: ${ACCOUNT_ID}"
if [ -z "${ACCOUNT_ID}" ]; then
  echo "No account matches username: ${GREETER_USERNAME}"
  exit 1
fi

echo "Renaming username from '${GREETER_USERNAME}' to '${USERNAME}'"

# MongoDB command to udpate the username in the account document with the specific account ID
UPDATE_COMMAND_FILE="/tmp/update-username-on-account.js"
cat >${UPDATE_COMMAND_FILE} <<EOF
use account
db.account.update({"_id" : ObjectId("${ACCOUNT_ID}")},{\$set: {"profile.username": "${USERNAME}"}});
EOF

UPDATE_QUERY_RESULT=$(${DIR}/mongodb.sh -c account-manager -d account -f ${UPDATE_COMMAND_FILE})
echo "$UPDATE_QUERY_RESULT" | grep "WriteResult"

