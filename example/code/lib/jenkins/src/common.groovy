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
