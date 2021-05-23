import groovy.json.JsonSlurper

svc_ids = groovy.json.JsonOutput.toJson(SERVICE_ID.split(","))


try {
    List<String> resultArray = new ArrayList<String>()
    url = 'http://qairon:5001/api/rest/v1/service'

    HttpURLConnection connection = new URL(url).openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        jsonSlurper = new JsonSlurper()
        // get the JSON response
        inStream = connection.inputStream
        services = jsonSlurper.parse(inStream).objects
        services.objects
        services.each { services -> resultArray.add(services.id) }
        connection.disconnect()

        return resultArray


    } else {
        print connection.responseCode + ": " + connection.inputStream.text

    }


} catch (e) {
    print(e)
}

