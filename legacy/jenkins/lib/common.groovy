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

def node_with_secrets = { name, nodeLabel, container, function ->
    timestamps {

        podTemplate(name: name, label: nodeLabel, yaml: """
kind: Pod
metadata:
  name: microservice-orchestration
spec:
  containers:
  - name: microservice-orchestration
    image: 407733091588.dkr.ecr.us-west-2.amazonaws.com/ego-cicd/microservice-orchestration:1.0.13
    imagePullPolicy: Always
    command:
    - /bin/cat
    tty: true
"""
        ) {
            node(nodeLabel) {
                def secrets = [[$class: 'VaultSecret', path: 'cicd/prod-1/aws_keys', secretValues: [
                        [$class: 'VaultSecretValue', envVar: 'AWS_ACCESS_KEY_ID_PROD', vaultKey: 'AWS_ACCESS_KEY_ID'],
                        [$class: 'VaultSecretValue', envVar: 'AWS_SECRET_ACCESS_KEY_PROD', vaultKey: 'AWS_SECRET_ACCESS_KEY']]],
                               [$class: 'VaultSecret', path: 'cicd/aws_keys', secretValues: [
                                       [$class: 'VaultSecretValue', envVar: 'AWS_ACCESS_KEY_ID_INT', vaultKey: 'AWS_ACCESS_KEY_ID'],
                                       [$class: 'VaultSecretValue', envVar: 'AWS_SECRET_ACCESS_INT', vaultKey: 'AWS_SECRET_ACCESS_KEY']]],
                               [$class: 'VaultSecret', path: 'cicd/bitbucket', secretValues: [
                                       [$class: 'VaultSecretValue', envVar: 'BITBUCKET_USER', vaultKey: 'BITBUCKET_USER'],
                                       [$class: 'VaultSecretValue', envVar: 'BITBUCKET_APP_PASSWORD', vaultKey: 'BITBUCKET_APP_PASSWORD']]],
                               [$class: 'VaultSecret', path: 'cicd/artifactory', secretValues: [
                                       [$class: 'VaultSecretValue', envVar: 'ART_TOOL_USER', vaultKey: 'ART_TOOL_USER'],
                                       [$class: 'VaultSecretValue', envVar: 'ART_TOOL_PASSWORD', vaultKey: 'ART_TOOL_PASSWORD'],
                                       [$class: 'VaultSecretValue', envVar: 'ART_BUILD_USER', vaultKey: 'ART_BUILD_USER'],
                                       [$class: 'VaultSecretValue', envVar: 'ART_BUILD_PASSWORD', vaultKey: 'ART_BUILD_PASSWORD']]],
                               [$class: 'VaultSecret', path: 'cicd/integration/user-manager', secretValues: [
                                       [$class: 'VaultSecretValue', envVar: 'GOOGLE_APPLICATION_CREDENTIALS', vaultKey: 'GOOGLE_APPLICATION_CREDENTIALS'],
                                       [$class: 'VaultSecretValue', envVar: 'GOOGLE_API_KEY', vaultKey: 'GOOGLE_API_KEY']]]]

                wrap([$class: 'VaultBuildWrapper', vaultSecrets: secrets]) {
                    properties([
                            parameters([string(defaultValue: '', description: 'Tested microservice name', name: 'APP_NAME', trim: true),
                                        string(defaultValue: '', description: 'Tested microservice version', name: 'APP_VERSION', trim: true),
                                        choice(choices: ['int-1', 'int-2', 'prod-1'], description: 'Against which environment microservice will be tested?', name: 'CLUSTER_NAME')]),
                            disableConcurrentBuilds()
                    ])
                    env.APP_NAME = "${params.APP_NAME}"
                    env.APP_VERSION = "${params.APP_VERSION}"
                    env.STACK_NAME = "env-${params.ENV_NAME}"
                    env.CLUSTER_NAME = "${params.CLUSTER_NAME}"
                    env.JOB_NAME = "${env.JOB_NAME}"
                    env.BUILD_NUMBER = "${env.BUILD_NUMBER}"
                    currentBuild.displayName = "#${env.BUILD_NUMBER} `${env.APP_NAME}-v${env.APP_VERSION}`"

                    stage('Configure aws account and kubectl config') {

                        container(container) {
                            function()
                        }


                    }

                }
            } // End timestamps
        }
    }
}
