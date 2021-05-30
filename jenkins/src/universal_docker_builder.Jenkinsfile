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
                ]

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

                    def command = $/
                        set -x
                        SERVICE_ID=$$(curl -s qairon:5001/api/rest/v1/service$/${svc_id})
                        echo $$SERVICE_ID
                    /$

                    sh script: command
                }
            }
        }
    }
}
parallel(jobs)