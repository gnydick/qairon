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
                        $class: 'CascadeChoiceParameter',
                        referencedParameters: 'SERVICES',
                        choiceType  : 'PT_SINGLE_SELECT',
                        description : 'Select the Builds from the Dropdown List',
                        filterLength: 3,
                        filterable  : true,
                        name        : 'BUILDS',
                        script      : [
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
                        $class: 'CascadeChoiceParameter',
                        referencedParameters: 'SERVICES',
                        choiceType  : 'PT_MULTI_SELECT',
                        description : 'Select the Builds from the Dropdown List',
                        filterLength: 3,
                        filterable  : true,
                        name        : 'DEPLOYMENTS',
                        script      : [
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
                ]

        ])
])


node('helm-installer') {
    container(name: 'helm') {
        stage(name: 'parallelize chart releases') {
            def deployment = params.DEPLOYMENT_ID
            def build = params.BUILD_ID
            def qairon = load("lib/qairon/main.groovy")

            def env_script = load("lib/qairon/environment_lookup.groovy")
            checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'main']], extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'nextgen/ops']]], [$class: 'RelativeTargetDirectory', relativeTargetDir: 'bitbucket']], userRemoteConfigs: [[credentialsId: 'jenkins-infra0-bitbucket', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

            build = qairon.get_builds(params.SERVICE_ID)
            print(build)


        }
    }
}