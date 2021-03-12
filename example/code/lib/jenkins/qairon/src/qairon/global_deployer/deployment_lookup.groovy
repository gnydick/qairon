import groovy.json.JsonSlurper

svc_ids = groovy.json.JsonOutput.toJson(SERVICE_ID.split(","))
rel_ids = groovy.json.JsonOutput.toJson(RELEASE_ID.split(","))


try {
    List<String> resultArray = new ArrayList<String>()
    url = 'http://qairon:5001/api/rest/v1/deployment?q={"filters":[{"name":"service_id","op":"in","val":'+ svc_ids + '},{"name":"release_id","op":"in","val":'+ rel_ids + '}]}'

    HttpURLConnection connection = new URL(url).openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        jsonSlurper = new JsonSlurper()
        // get the JSON response
        inStream = connection.inputStream
        deployments = jsonSlurper.parse(inStream).objects
        deployments.objects
        deployments.each { deployment  -> resultArray.add(deployment.id)}
        connection.disconnect()

        return resultArray


    } else {
        print connection.responseCode + ": " + connection.inputStream.text

    }



} catch (e) {
    print(e)
}


