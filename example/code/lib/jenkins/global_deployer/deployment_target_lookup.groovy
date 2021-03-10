import groovy.json.JsonSlurper
import java.util.logging.Logger

Logger logger = Logger.getLogger('org.biouno.unochoice')

envs = groovy.json.JsonOutput.toJson(ENVIRONMENTS.split(","))
logger.info(envs)

try {
    List<String> resultArray = new ArrayList<String>()
    url = 'http://qairon:5001/api/rest/v1/deployment_target?q={"filters":[{"name":"environment_id","op":"in","val":'+ envs + '}]}'
    logger.info(url)
    HttpURLConnection connection = new URL(url).openConnection()
    connection.connect()
    if (connection.responseCode == 200) {
        jsonSlurper = new JsonSlurper()
        // get the JSON response
        inStream = connection.inputStream
        stacks = jsonSlurper.parse(inStream).objects
        stacks.objects
        stacks.each { stack  -> resultArray.add(stack.id)}
        connection.disconnect()

        return resultArray


    } else {
        print connection.responseCode + ": " + connection.inputStream.text

    }



} catch (e) {
    print(e)
}

