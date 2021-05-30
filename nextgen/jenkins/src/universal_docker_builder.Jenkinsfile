properties([
        parameters([
                [
                        $class      : 'ChoiceParameter',
                        choiceType  : 'PT_MULTI_SELECT',
                        description : 'Select the Service from the Dropdown List',
                        filterLength: 3,
                        filterable  : true,
                        name        : 'SERVICES',
                        script      : [
                                $class: 'GroovyScript',
                                script: [
                                        classpath: [],
                                        sandbox  : false,
                                        script   :
                                                $/
package lib.qairon

import groovy.json.JsonSlurper


try {
    List<String> resultArray = new ArrayList<String>()
    HttpURLConnection connection = new URL("http://qairon:5001/api/rest/v1/service").openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        jsonSlurper = new JsonSlurper()
        // get the JSON response
        inStream = connection.inputStream
        services = jsonSlurper.parse(inStream).objects
        services.objects
        services.each { service  -> resultArray.add(service.id)}
        connection.disconnect()

        return resultArray
    } else {
        print connection.responseCode + ": " + connection.inputStream.text
    }
} catch (e) {
    print(e)
}
/$
                                ]
                        ]
                ],
                string(name: 'REPO', defaultValue: '', description: 'Git Repo', trim: true),
                string(name: 'DOCKERFILE_PATH', defaultValue: '', description: 'Where to find the Dockerfile in the repo and the filename itself', trim: true),
                string(name: 'REGISTRY', defaultValue: '', description: '', trim: true),
                string(name: 'BRANCH', defaultValue: '', description: '', trim: true),
                string(name: 'IMMUTABLE_VCS_TAG', defaultValue: '', trim: true),
                credentials(credentialType: 'com.cloudbees.plugins.credentials.common.StandardCredentials', defaultValue: '', description: '', name: 'GIT_CREDS', required: true)


        ])
])


def jobs = [:]

def svc_ids = SERVICES.split(",")

for (int i = 0; i < svc_ids.size(); i++) {
    def index = i
    def svc_id = svc_ids[index]
    println(svc_ids[index])
    jobs[svc_id] = {
        node('docker-builder') {
            container(name: 'docker-builder') {
                stage(name: 'checkout') {
                    def scmVars = checkout changelog: false, poll: false,
                            scm: [$class                           : 'GitSCM', branches: [[name: params.BRANCH]],
                                  doGenerateSubmoduleConfigurations: false,
                                  submoduleCfg                     : [],
                                  userRemoteConfigs                : [
                                          [credentialsId: params.GIT_CREDS, url: params.REPO]]]

                }
                stage('build and push'){
                    def fields = svc_id.split(':')
                    def image = params.REGISTRY + "/" + fields[-1] + ":" + env.BUILD_NUMBER
                    def command = $/
                    docker build -t $image --network=host ${params.DOCKERFILE_PATH}
                    aws ecr get-login-password  | docker login --username AWS --password-stdin $params.REGISTRY
                    docker push $image
                    /$
                    sh script: command
                }
                stage('record build') {
                    def data = $/
{
    "service_id": "${svc_id}",
    "build_num": "${env.BUILD_NUMBER}",
    "git_tag": "${params.IMMUTABLE_VCS_TAG}"
}
/$
                    def command = $/
curl -s -X POST -d '${data}' \
-H "Content-Type: application/json" \
http://qairon:5001/api/rest/v1/build
                    /$

                    sh script: command
                }
            }
        }
    }
}
parallel(jobs)