package base_jobs

properties([
        parameters([
                [
                        $class      : 'ChoiceParameter',
                        choiceType  : 'PT_SINGLE_SELECT',
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
                                                $/package lib.qairon

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
                [
                        $class              : 'CascadeChoiceParameter',
                        referencedParameters: 'SERVICES',
                        choiceType          : 'PT_SINGLE_SELECT',
                        description         : 'Select the Builds from the Dropdown List',
                        filterLength        : 3,
                        filterable          : true,
                        name                : 'BUILDS',
                        script              : [
                                $class: 'GroovyScript',
                                script: [
                                        classpath: [],
                                        sandbox  : false,
                                        script   :
                                                $/
                                                package lib.qairon

import groovy.json.JsonSlurper

svc_ids = groovy.json.JsonOutput.toJson(SERVICES.split(","))


try {
    List<String> resultArray = new ArrayList<String>()
    url = 'http://qairon:5001/api/rest/v1/build?q={"filters":[{"name":"service_id","op":"in","val":' + svc_ids + '}]}'

    HttpURLConnection connection = new URL(url).openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        def jsonSlurper = new JsonSlurper()
        // get the JSON response
        def inStream = connection.inputStream
        def builds = jsonSlurper.parse(inStream).objects
        builds.objects
        builds.each { build -> resultArray.add(build.id) }
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
                [
                        $class              : 'CascadeChoiceParameter',
                        referencedParameters: 'SERVICES',
                        choiceType          : 'PT_MULTI_SELECT',
                        description         : 'Select the Deployments from the Dropdown List',
                        filterLength        : 3,
                        filterable          : true,
                        name                : 'DEPLOYMENTS',
                        script              : [
                                $class: 'GroovyScript',
                                script: [
                                        classpath: [],
                                        sandbox  : false,
                                        script   :
                                                $/
                                                package lib.qairon

import groovy.json.JsonSlurper

svc_ids = groovy.json.JsonOutput.toJson(SERVICES.split(","))


try {
    List<String> resultArray = new ArrayList<String>()
    url = 'http://qairon:5001/api/rest/v1/deployment?q={"filters":[{"name":"service_id","op":"in","val":' + svc_ids + '}]}'

    HttpURLConnection connection = new URL(url).openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        def jsonSlurper = new JsonSlurper()
        // get the JSON response
        def inStream = connection.inputStream
        def deployments = jsonSlurper.parse(inStream).objects
        deployments.objects
        deployments.each { deployment -> resultArray.add(deployment.id) }
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
                ]

        ])
])

def dep_ids = DEPLOYMENTS.split(",")


def jobs = [:]
for (int i = 0; i < dep_ids.size(); i++) {
    def index = i
    def dep_id = dep_ids[index]
    println(dep_ids[index])

    jobs[dep_id] = {

        node('helm-installer') {
            container(name: 'helm') {
                stage(name: 'parallelize chart releases') {
                    checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'main']], extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'nextgen/helm/charts'], [path: 'nextgen/ops']]], [$class: 'RelativeTargetDirectory', relativeTargetDir: 'bitbucket']], userRemoteConfigs: [[credentialsId: 'jenkins-infra0-bitbucket', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

                    def command = $/
                set -x
                DEP_DESCRIPTOR=$$(curl -s qairon:5001/api/rest/v1/deployment$/${dep_id})
                SERVICE_ID=$$(echo $$DEP_DESCRIPTOR | jq -r .service.id)
                SERVICE_NAME=$$(echo $$DEP_DESCRIPTOR | jq -r .service.name)
                DEP_TARGET=$$(echo $$DEP_DESCRIPTOR | jq -r .deployment_target)
                DEP_TGT_NAME=$$(echo $$DEP_TARGET | jq -r .name)
                PARTITION_ID=$$(echo $$DEP_TARGET | jq -r .partition_id)
                PARTITION=$$(curl -s qairon:5001/api/rest/v1/partition$/$$PARTITION_ID)
                REGION_OBJ=$$(echo $$PARTITION | jq -r .region)
                REGION=$$(echo $$REGION_OBJ | jq -r .name)
                POP_ID=$$(echo $$REGION_OBJ | jq -r .pop_id)
                POP=$$(curl -s qairon:5001/api/rest/v1/pop$/$$POP_ID)
                ACCOUNT=$$(echo $$POP | jq -r .native)
                PROVIDER=$$(echo $$POP | jq -r .pop_type_id)
                
                REPO_URL=$(curl -s qairon:5001/api/rest/v1/service$/$$SERVICE_ID/repos | jq -r '.objects[]|select(.repo_type_id == "helm")|.url')

     
                mkdir tmp
                rsync -var bitbucket/nextgen/helm/charts$/$$SERVICE_NAME/ tmp$/$$SERVICE_NAME/
                cp bitbucket/nextgen/ops$/$$PROVIDER$/$$ACCOUNT$/$$REGION$/$$DEP_TGT_NAME/helm$/$${SERVICE_NAME}.yaml \
                    tmp$/$$SERVICE_NAME/values.yaml
    
                cd tmp
                sed -i "s/%--tag--%$/$$BUILD_NUMBER/g" $$SERVICE_NAME/values.yaml
                echo -e"\nversion: $$BUILD_NUMBER" >> $$SERVICE_NAME/Chart.yaml
                helm package --version $$BUILD_NUMBER $$SERVICE_NAME
                aws s3 cp $$SERVICE_NAME-$$BUILD_NUMBER.tgz $$REPO_URL$/${dep_id}$/$$SERVICE_NAME-$$BUILD_NUMBER.tgz
               
            /$
                sh script: command
                }
                stage('record release') {
                    def data = $/
{
    "build_id": "${params.BUILDS}",
    "build_num": "${env.BUILD_NUMBER}",
    "deployment_id": "${dep_id}"
}
/$
                    def command = $/
curl -s -X POST -d '${data}' \
-H "Content-Type: application/json" \
http://qairon:5001/api/rest/v1/release
                    /$

                    sh script: command
                }
            }
        }
    }
}

parallel(jobs)
