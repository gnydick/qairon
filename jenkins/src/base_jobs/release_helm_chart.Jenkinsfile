package base_jobs

def deployment = params.DEPLOYMENT_ID
def build = params.BUILD_ID
def qairon = load("lib/qairon/main.groovy")

properties([
        parameters([
                [
                        $class    : 'ChoiceParameter',
                        choiceType: 'PT_SINGLE_SELECT',
                        name      : 'ENVIRONMENT',
                        script    : [
                                $/
try {
    List<String> resultArray = new ArrayList<String>()
    HttpURLConnection connection = new URL("http://qairon:5001/api/rest/v1/environment").openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        jsonSlurper = new JsonSlurper()
        // get the JSON response
        inStream = connection.inputStream
        environments = jsonSlurper.parse(inStream).objects
        environments.objects
        environments.each { environment  -> resultArray.add(environment.id)}
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
        ])
])


node('helm-installer') {
    container(name: 'helm')
    stage(name: 'parallelize chart releases') {
        checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'main']], extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'nextgen/ops']]], [$class: 'RelativeTargetDirectory', relativeTargetDir: 'bitbucket']], userRemoteConfigs: [[credentialsId: 'jenkins-infra0-bitbucket', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

        build = qairon.get_builds(params.SERVICE_ID)
        print(build)


    }
}
