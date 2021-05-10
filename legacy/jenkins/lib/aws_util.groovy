package lib

def assume_and_sh(envrn, role, credentials, shell_cmd) {
    def account_id = account_from_environment(envrn)
    def result = ""
    withCredentials(credentials) {
        result = sh(script: """
            set +x
            unset AWS_ACCESS_KEY_ID && unset AWS_SECRET_ACCESS_KEY && unset AWS_SESSION_TOKEN && unset AWS_SECURITY_TOKEN

            session_json=\$(aws sts assume-role --role-arn arn:aws:iam::${account_id}:role/${role} \
            --role-session-name jenkins-${env.JOB_BASE_NAME}-${env.BUILD_NUMBER})

            export AWS_ACCESS_KEY_ID=\$(echo \${session_json} |jq -r '.Credentials.AccessKeyId')
            export AWS_SECRET_ACCESS_KEY=\$(echo \${session_json} |jq -r '.Credentials.SecretAccessKey')
            export AWS_SESSION_TOKEN=\$(echo "\${session_json}"| jq -r '.Credentials.SessionToken')
        """ + shell_cmd, returnStdout: true)
    }

    return result
}

def sh_for_assumed_role(account_id, role, shell) {
    def result = ""
    withCredentials([
            [$class       : 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_ACCESS_KEY_ID',
             credentialsId: 'aws-null', secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'],
            [$class       : 'AmazonWebServicesCredentialsBinding', accessKeyVariable: 'AWS_SESSION_TOKEN',
             credentialsId: 'aws-null', secretKeyVariable: 'AWS_SECURITY_TOKEN']]) {
        result = sh(script: """
            set +x
            unset AWS_ACCESS_KEY_ID && unset AWS_SECRET_ACCESS_KEY && unset AWS_SESSION_TOKEN && unset AWS_SECURITY_TOKEN

            session_json=\$(aws sts assume-role --role-arn arn:aws:iam::${account_id}:role/${role} \
            --role-session-name jenkins-${env.JOB_BASE_NAME}-${env.BUILD_NUMBER})

            export AWS_ACCESS_KEY_ID=\$(echo \${session_json} |jq -r '.Credentials.AccessKeyId')
            export AWS_SECRET_ACCESS_KEY=\$(echo \${session_json} |jq -r '.Credentials.SecretAccessKey')
            export AWS_SESSION_TOKEN=\$(echo "\${session_json}"| jq -r '.Credentials.SessionToken')
        """ + shell, returnStdout: true)
    }

    return result
}





return this
