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

}

def getSecrets() {
    return [[$class: 'VaultSecret', path: 'cicd/prod-1/aws_keys', secretValues: [
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
}

return this;