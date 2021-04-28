package lib.qairon

import groovy.json.JsonSlurper



ArrayList<String> query(String resource, String filter) {
    try {
        ArrayList<String> resultArray = new ArrayList<String>()

        def url = "http://qairon:5001/api/rest/v1/${resource}?q={\"filters\":${filter}}"

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


    } catch (Exception e) {
        print(e.message)
    }
}