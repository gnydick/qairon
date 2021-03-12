package GlobalDeployer

import groovy.json.JsonSlurper

//URLEncoder.encode(
//        "prod1:infra:observ:bosun:default:configmap:alerts:default",
//        'UTF-8')

    def app="infra"
    try {
        List<String> resultArray = new ArrayList<String>()
        HttpURLConnection connection = new URL("http://qairon:5001/api/rest/v1/application/${app}/stacks").openConnection()
        connection.connect()
        if (connection.responseCode == 200) {
            jsonSlurper = new JsonSlurper()
            // get the JSON response
            inStream = connection.inputStream
            stacks = jsonSlurper.parse(inStream).objects
            stacks.objects
//            def result = new String[stacks.size()]
            stacks.each { stack  -> resultArray.add(stack.id)}
            connection.disconnect()
            results = resultArray.join(', ')
            return results
            

        } else {
            print connection.responseCode + ": " + connection.inputStream.text

        }
       

        /*    boilerplate = readFile encoding: 'UTF-8', file: 'bosun/templates/configmap-alerts.yaml'
              writeFile encoding: 'UTF-8', file: 'bosun/templates/configmap-alerts.yaml', text: "'${config}\n${boilerplate}'"
              completeFile = readFile encoding: 'UTF-8', fil */
    } catch (e) {
        print(e)
    }

