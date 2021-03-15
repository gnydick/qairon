

svc_ids = groovy.json.JsonOutput.toJson(SERVICE_ID.split(","))
def common = load "${WORKSPACE}/withme-ops/example/code/lib/jenkins/common.groovy"
def base = load "${WORKSPACE}/withme-ops/example/code/lib/jenkins/base.groovy"

return base.query('build',"[{\"name\":\"service_id\",\"op\":\"in\",\"val\":'+ svc_ids + '}]")
