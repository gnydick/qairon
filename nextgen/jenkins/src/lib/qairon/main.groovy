package lib.qairon

import groovy.json.JsonSlurper

def get_builds(service_ids) {
    try {
        List<String> resultArray = new ArrayList<String>()
        url = 'http://qairon:5001/api/rest/v1/build?q={"filters":[{"name":"service_id","op":"in","val":' + service_id + '}]}'
        HttpURLConnection connection = new URL(url).openConnection()
        connection.connect()
        if (connection.responseCode == 200) {
            def jsonSlurper = new JsonSlurper()
            // get the JSON response
            def inStream = connection.inputStream
            def builds = jsonSlurper.parse(inStream).objects
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
}

def get_deployments_here(dep_target_ids) {
    try {
        List<String> resultArray = new ArrayList<String>()
        url = 'http://qairon:5001/api/rest/v1/deployment?q={"filters":[{"name":"deployment_target_id","op":"in","val":' + dep_target_ids + '}]}'
        HttpURLConnection connection = new URL(url).openConnection()
        connection.connect()
        if (connection.responseCode == 200) {
            jsonSlurper = new JsonSlurper()
            // get the JSON response
            inStream = connection.inputStream
            deployments = jsonSlurper.parse(inStream).objects
            deployments.objects
            deployments.each { deployment -> resultArray.add(deployment.id) }
            connection.disconnect()
            return resultArray
        } else {
            print connection.responseCode + ": " + connection.inputStream.text
        }
    } catch (e) {
        print(e)
    }
}

def get_deployment_targets_for_envs(env_ids) {
    try {
        List<String> resultArray = new ArrayList<String>()
        url = 'http://qairon:5001/api/rest/v1/deployment_target?q={"filters":[{"name":"environment_id","op":"in","val":' + env_ids + '}]}'
        logger.info(url)
        HttpURLConnection connection = new URL(url).openConnection()
        connection.connect()
        if (connection.responseCode == 200) {
            jsonSlurper = new JsonSlurper()
            // get the JSON response
            inStream = connection.inputStream
            stacks = jsonSlurper.parse(inStream).objects
            stacks.objects
            stacks.each { stack -> resultArray.add(stack.id) }
            connection.disconnect()
            return resultArray
        } else {
            print connection.responseCode + ": " + connection.inputStream.text
        }
    } catch (e) {
        print(e)
    }
}

def get_envs_list() {
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
            environments.each { environment -> resultArray.add(environment.id) }
            connection.disconnect()
            return resultArray
        } else {
            print connection.responseCode + ": " + connection.inputStream.text
        }
    } catch (e) {
        print(e)
    }
}

def get_releases(build_ids) {
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
}

def get_stack_services(stack_id) {
    try {
        List<String> resultArray = new ArrayList<String>()
        HttpURLConnection connection = new URL("http://qairon:5001/api/rest/v1/stack/${stack_id}/services").openConnection()
        connection.connect()
        if (connection.responseCode == 200) {
            jsonSlurper = new JsonSlurper()
            // get the JSON response
            inStream = connection.inputStream
            services = jsonSlurper.parse(inStream).objects
            services.objects
            services.each { service -> resultArray.add(service.id) }
            connection.disconnect()
            return resultArray
        } else {
            print connection.responseCode + ": " + connection.inputStream.text
        }
    } catch (e) {
        print(e)
    }
}

def get_app_stacks(app_id) {
    try {
        List<String> resultArray = new ArrayList<String>()
        HttpURLConnection connection = new URL("http://qairon:5001/api/rest/v1/application/${app_id}/stacks").openConnection()
        connection.connect()
        if (connection.responseCode == 200) {
            jsonSlurper = new JsonSlurper()
            // get the JSON response
            inStream = connection.inputStream
            stacks = jsonSlurper.parse(inStream).objects
            stacks.objects
//            def result = new String[stacks.size()]
            stacks.each { stack -> resultArray.add(stack.id) }
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
}