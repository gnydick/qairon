import groovy.json.JsonSlurper

build_ids = groovy.json.JsonOutput.toJson(BUILD_ID.split(","))


try {
    List<String> resultArray = new ArrayList<String>()
    url = 'http://qairon:5001/api/rest/v1/release?q={"filters":[{"name":"build_id","op":"in","val":' + build_ids + '}]}'


    HttpURLConnection connection = new URL(url).openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        jsonSlurper = new JsonSlurper()
        // get the JSON response
        inStream = connection.inputStream
        releases = jsonSlurper.parse(inStream).objects
        releases.objects
        releases.each { release -> resultArray.add(release.id) }
        connection.disconnect()

        return resultArray


    } else {
        print connection.responseCode + ": " + connection.inputStream.text

    }


} catch (e) {
    print(e)
}

