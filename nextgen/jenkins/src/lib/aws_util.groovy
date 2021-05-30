package lib

/*

Erases and sets the AWS credentials via environment variables
then runs a shell command.

Stdout is always returned, just don't consume it if not needed.
-----
shell_cmd: string passed to the 'sh' command


 */

def set_aws_creds_and_sh(shell_cmd) {
    def result = ""

    result = sh(script: """
        set +x
        unset AWS_ACCESS_KEY_ID && unset AWS_SECRET_ACCESS_KEY && unset AWS_SESSION_TOKEN && unset AWS_SECURITY_TOKEN
        export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID_INT}
        export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_INT}
    """ + shell_cmd, returnStdout: true)


    return result
}


return this
