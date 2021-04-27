

import groovy.json.JsonSlurper


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

