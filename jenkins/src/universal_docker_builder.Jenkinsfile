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
                stage(name: 'parallelize docker builds') {

                    def scmVars = checkout changelog: false, poll: false,
                            scm: [$class                           : 'GitSCM', branches: [[name: params.BRANCH]],
                                  doGenerateSubmoduleConfigurations: false,
                                  submoduleCfg                     : [],
                                  userRemoteConfigs                : [
                                          [credentialsId: params.GIT_CREDS, url: params.REPO]]]

                    def builtImage = docker.build("${params.REGISTRY}/${params.REPO}:${env.BUILD_ID}", params.DOCKERFILE_PATH)


                }
            }
        }
    }
}
parallel(jobs)