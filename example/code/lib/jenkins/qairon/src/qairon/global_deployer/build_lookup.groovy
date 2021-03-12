package qairon.global_deployer

import groovy.json.JsonSlurper

svc_ids = groovy.json.JsonOutput.toJson(SERVICE_ID.split(","))

qairon = load "../qairon/base.groovy"

try {
    List<String> resultArray = new ArrayList<String>()
    url = 'http://qairon:5001/api/rest/v1/build?q={"filters":[{"name":"service_id","op":"in","val":' + svc_ids + '}]}'

    HttpURLConnection connection = new URL(url).openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        jsonSlurper = new JsonSlurper()
        // get the JSON response
        inStream = connection.inputStream
        builds = jsonSlurper.parse(inStream).objects
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

