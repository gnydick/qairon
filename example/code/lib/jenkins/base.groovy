package qairon

import groovy.json.JsonSlurper
@Library('qairon')
import qairon.QueryFilter


ArrayList<String> query(String resource, QueryFilter filter) {
    try {
        ArrayList<String> resultArray = new ArrayList<String>()
        def filterString = filter.getFilter()
        def url = "http://qairon:5001/api/rest/v1/${resource}?q={\"filters\":${filterString}}"

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