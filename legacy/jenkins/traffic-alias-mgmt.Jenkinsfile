timestamps {
    podTemplate(name: 'test', label: 'test', yaml: """
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
        node('test') {


            stage('Configure aws account and kubectl config') {
                container('microservice-orchestration') {
                    checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'features/JENK-GAMELIFT']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'legacy/jenkins'], [path: 'legacy/sceptre']]]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'bitbckt-org-wm-bldr', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

                    def commonLib = load "${WORKSPACE}/legacy/jenkins/lib/common.groovy"
                    def awsLib = load "${WORKSPACE}/legacy/jenkins/lib/aws_util.groovy"
                    def secrets = commonLib.getSecrets()


                    wrap([$class: 'VaultBuildWrapper', vaultSecrets: secrets]) {
                        properties([
                                parameters([choice(choices: ['--Choose--', 'launch', 'delete', 'update'], description: 'Action to take', name: 'SCEPTRE_ACTION'),
                                            string(defaultValue: '', description: 'GameLift Alias Name', name: 'ALIAS_NAME', trim: true),
                                            choice(choices: ['us-west-2'], description: 'AWS Region - us-west-2 is default', name: 'AWS_REGION'),
                                            choice(choices: ['int-3', 'int-1', 'int-2', 'prod-1'], description: 'Against which environment microservice will be tested?', name: 'ENVIRONMENT')]),
                                disableConcurrentBuilds()
                        ])


                        def cmd = """
                             cd ${WORKSPACE}/legacy/sceptre/aws
                             export GAMELIFT_BUILD_ID=${GAMELIFT_BUILD_ID}
                             sceptre  --var-file varfiles/${AWS_REGION}/${ENVIRONMENT}/traffic-alias.yaml  ${SCEPTRE_ACTION} ${AWS_REGION}/gamelift-update-alias -y
                        """

                        awsLib.set_aws_creds_and_sh(cmd)
                    }


                }

            }
        }
    }
}
