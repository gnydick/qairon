package lib

def notifySlack(String buildStatus = 'STARTED', String channel, String color = null, String message = null) {

    // Build status of null means success.
    buildStatus = buildStatus ?: 'SUCCESS'
    def icons
    if (buildStatus == 'STARTED') {
        icons = ':biking:'
    } else if (buildStatus == 'SUCCESS') {
        icons = ':pusheen_dancing:'
    } else if (buildStatus == 'ABORTED') {
        icons = ':thinking_face:'
    } else {
        icons = ':twitching:'
    }
    if (color.equals(null)) {
        if (buildStatus == 'STARTED') {
            color = '#D4DADF'
        } else if (buildStatus == 'SUCCESS') {
            color = '#BDFFC3'
        } else if (buildStatus == 'ABORTED') {
            color = '#FFFE89'
        } else {
            color = '#FF9FA1'
        }
    }
    def msg = "${buildStatus}${icons}: `${env.JOB_NAME}`\n ${env.BUILD_DISPLAY_NAME}:\n<${env.BUILD_URL}console|Watch build console output> @here"
    if (!message.equals(null)) {
        msg <<= "\n"
        msg <<= message
    }
    slackSend(color: color, channel: channel, message: msg)
}

def node_with_secrets(nodeLabel, container, function) {
    node(nodeLabel) {
        try {
            def secrets = [[$class: 'VaultSecret', path: 'cicd/aws_keys', secretValues: [
                    [$class: 'VaultSecretValue', envVar: 'AWS_ACCESS_KEY_ID', vaultKey: 'AWS_ACCESS_KEY_ID'],
                    [$class: 'VaultSecretValue', envVar: 'AWS_SECRET_ACCESS_KEY', vaultKey: 'AWS_SECRET_ACCESS_KEY']]],
                           [$class: 'VaultSecret', path: 'cicd/bitbucket', secretValues: [
                                   [$class: 'VaultSecretValue', envVar: 'BITBUCKET_USER', vaultKey: 'BITBUCKET_USER'],
                                   [$class: 'VaultSecretValue', envVar: 'BITBUCKET_APP_PASSWORD', vaultKey: 'BITBUCKET_APP_PASSWORD']]]]
            wrap([$class: 'VaultBuildWrapper', vaultSecrets: secrets]) {
                properties([disableConcurrentBuilds()])
                stage('Configure tools') {
                    notifySlack()
                    slackSend color: 'good', message: "`${env.JOB_NAME}` #${env.BUILD_NUMBER}\nRunning 'Configure tools' stage."
                    container(name: container) {
                        function(params)
                    }
                }
            }
        }
        catch (e) {
            currentBuild.result = 'FAILURE'
            throw e
        } finally {
            notifySlack(currentBuild.result)
        }
    }
}

