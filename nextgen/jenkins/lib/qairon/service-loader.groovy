

import groovy.json.JsonSlurper


try {
    List<String> resultArray = new ArrayList<String>()
    HttpURLConnection connection = new URL("http://qairon:5001/api/rest/v1/stack/${STACK}/services").openConnection()
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

