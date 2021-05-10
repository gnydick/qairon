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
                    checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'features/JENK-GAMELIFT']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'legacy/jenkins']]]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'bitbckt-org-wm-bldr', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

                    def commonLib = load "${WORKSPACE}/legacy/jenkins/lib/common.groovy"
                    def secrets = commonLib.getSecrets()


                    wrap([$class: 'VaultBuildWrapper', vaultSecrets: secrets]) {
                        properties([
                                parameters([string(defaultValue: '', description: 'Tested microservice name', name: 'APP_NAME', trim: true),
                                            string(defaultValue: '', description: 'Tested microservice version', name: 'APP_VERSION', trim: true),
                                            choices(choices: ['us-west-2'], defaultValue: 'us-west-2', description: 'AWS Region', name: 'AWS_REGION', trim: true),
                                            choices(choices: ['int-3', 'int-1', 'int-2', 'prod-1'], defaultValue: 'int-3', description: 'Against which environment microservice will be tested?', name: 'CLUSTER_NAME')]),
                                disableConcurrentBuilds()
                        ])
                        env.APP_NAME = "${params.APP_NAME}"
                        env.APP_VERSION = "${params.APP_VERSION}"
                        env.STACK_NAME = "env-${params.ENV_NAME}"
                        env.CLUSTER_NAME = "${params.CLUSTER_NAME}"
                        env.JOB_NAME = "${env.JOB_NAME}"
                        env.BUILD_NUMBER = "${env.BUILD_NUMBER}"
                        currentBuild.displayName = "#${env.BUILD_NUMBER} `${env.APP_NAME}-v${env.APP_VERSION}`"
                        sh """
                             cd ${WORKSPACE}/legacy/sceptre/aws
                             sceptre  --var-file varfiles/${REGION}/${CLUSTER_NAME}/fleet  launch us-west-2/gamelift-create-fleet
                        """


                    }


                }

            }
        }
    }
}
