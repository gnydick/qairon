#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cGUiOiJKV1QiLCJraWQiOiJXaXRobWUifQ.eyJpc3MiOiJodHRwczovL2F1dGgud2l0aG1lLmNvbS8iLCJzdWIiOiJXaXRobWUiLCJhdWQiOiJXaXRobWUiLCJpYXQiOjE1Mzg3OTAwNzIsInNjb3BlIjoiYXV0aCJ9.YkSig8XvrDocmjeJLLCMRK8QgN6SolVWKtVA9X9mqYoQ1BqJki0cYdtpIiKetbzPcnTMezuUXjkjpcb7iUfvsw"

# Make sure jq is installed
WHICH_JQ=$(which jq)
if [ -z "${WHICH_JQ}" ]; then
  echo "This script uses the jq command to parse JSON.  Please install it from here: https://stedolan.github.io/jq/download/"
  exit 1
fi
echo "jq --version"
jq --version || { echo "test-leaderboard-configmap-withme: Error calling jq [${WHICH_JQ}]"; exit 1; }

# Print help
function help() {
  echo usage: test-leaderboard-configmap-withme.sh
  echo " -h <arg>"
  echo " --host <arg>             The main subdomain for REST entry points for the environment"
  echo
  echo " -r <arg>"
  echo " -rules_config_map <arg>  The path to the rules Config Map YAML file"
  echo
  echo " -t <arg>"
  echo " --test_json <arg>        The path to the test suite JSON file"
  echo
  exit 1
}

function validate_http_status() {
  local _tokenResp=$1
  local _httpStatus=`echo "${_tokenResp}" | grep 'HTTP' | grep -v '100 Continue' | sed 's|[^ ]* \([0-9]*\).*|\1|'`
  echo "Http Status: [${_httpStatus}]"
  if [ "${_httpStatus}" != 200 ]; then
    if [ "${_httpStatus}" == 401 ]; then
      # Assume the token expired
      rm ${DIR}/publish.jwt 2> /dev/null
    fi
    local _errorHeader=`echo "${_tokenResp}" | grep 'WWW-Authenticate' | grep 'error'`
    if [ -z "${_errorHeader}" ]; then
      echo "${_tokenResp}"
      exit 1
    fi
    echo "${_errorHeader}"
    exit 1
  fi
}

# Issue curl request to Authentication Server
function authn_request() {
  local _resultName=$1
  local _curlCmd=$2
  local _tokenHeader=$3
  if [ -f "${DIR}/service-gateway.pem" ]; then
    local _tokenResp=`curl -i -s --cacert ${DIR}/service-gateway.pem "${_curlCmd}" -H "${_tokenHeader}"`
  else
    local _tokenResp=`curl -i -s "${_curlCmd}" -H "${_tokenHeader}"`
  fi

  echo ${_tokenResp}
  validate_http_status "${_tokenResp}"
  local _token=`echo ${_tokenResp} | sed 's|.*"token":"\([^"]*\).*|\1|'`
  if [ -z "${_token}" ]; then
    echo "Error retrieving App Token"
    exit 1
  fi
  eval $_resultName="'$_token'"
}

APP_ID="Withme"
TENANT="Withme"

# Parse command line arguments
while [[ $# -gt 1 ]]
do
key="$1"

case $key in
    -h|--host)
    HOST="$2"
    shift # past argument
    ;;
    -r|--rules_config_map)
    CONFIG_MAP_FILE="$2"
    shift # past argument
    ;;
    -t|--test_json)
    TEST_SUITE_JSON_FILE="$2"
    shift # past argument
    ;;
    *)
            # unknown option
    ;;
esac
shift
done

# Validate command line arguments
if [ -z "${HOST}" ]; then
  echo Missing --host argument
  help
fi
if [ -z "${CONFIG_MAP_FILE}" ]; then
  echo Missing --rules_config_map argument
  help
fi
if [ -z "${TEST_SUITE_JSON_FILE}" ]; then
  echo Missing --test_json argument
  help
fi
echo

if [ ! -f "${CONFIG_MAP_FILE}" ]; then
  echo "test-leaderboard-configmap-withme.sh: rule_config_map file invalid [${CONFIG_MAP_FILE}]"
  exit 1
fi
if [ ! -f "${TEST_SUITE_JSON_FILE}" ]; then
  echo "test-leaderboard-configmap-withme.sh: test_json file invalid [${TEST_SUITE_JSON_FILE}]"
  exit 1
fi

# Strip of everything from the Config Map up to and including the line with the field, "data:"
PROPERTIES_YAML=$(cat ${CONFIG_MAP_FILE} | sed '1,/^data:.*$/d' | sed 1d)

# Left justify the indentation so the YAML looks right and write it to a temp file
PROPERTIES_INDENT=$(echo "${PROPERTIES_YAML}" | head -1 | sed 's/\( *\).*/\1/')
INDENT_COUNT=$(echo -n "${PROPERTIES_INDENT}" | wc -c)
COLUMN=$((${INDENT_COUNT} + 1))
LEFT_JUSTIFIED_PROPERTIES_YAML=$(echo "${PROPERTIES_YAML}" | cut -c ${COLUMN}-)
echo "${LEFT_JUSTIFIED_PROPERTIES_YAML}" > /tmp/tmp.yaml

# Get an Auth Token from the App Token
echo "Retrieve Auth Token..."
INSTANCE=`date +%s`
authn_request AUTH_TOKEN "https://${HOST}/authn/v1/token/auth?instance_id=${INSTANCE}&app_class=${APP_ID}&tenant_id=${TENANT}" "Authorization: Bearer $APP_TOKEN"
echo

# Issue the upload request.  The service-gateway.pem is used for the local environment.
if [ -f "${DIR}/service-gateway.pem" ]; then
  TEST_RESPONSE=$(curl -s -i --cacert ${DIR}/service-gateway.pem -F "rulesYaml=@/tmp/tmp.yaml" -F "testsJson=@${TEST_SUITE_JSON_FILE}" "https://${HOST}/leaderboard/v1/metrics/validate" -H "Authorization: Bearer ${AUTH_TOKEN}")
else
  TEST_RESPONSE=$(curl -s -i -F "rulesYaml=@/tmp/tmp.yaml" -F "testsJson=@${TEST_SUITE_JSON_FILE}" "https://${HOST}/leaderboard/v1/metrics/validate" -H "Authorization: Bearer ${AUTH_TOKEN}")
fi

# Handle any errors
ERROR_MSG=$(echo "${TEST_RESPONSE}" | grep 'warning: 299')
if [ -z "${ERROR_MSG}" ]; then
  echo "REST request successful"
else
  echo "${TEST_RESPONSE}"
  exit 1
fi

# Write out a report
TEST_REPORT=$(echo "${TEST_RESPONSE}" | sed -n '/^{"testSuiteName.*$/,$p')
echo "${TEST_REPORT}" | jq '.testSuiteName'
echo "${TEST_REPORT}" | jq '.ruleTestCaseReports[]' | sed 's|\\n|\n|g'
echo "Test Summary:"
echo "${TEST_REPORT}" | jq '.ruleTestCaseReports[] | {(.testCaseName): (.validationPassed)}' | grep ':'
