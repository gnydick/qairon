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
                    def actions_requiring_confirmation = ['launch', 'update', 'delete']

                    checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'features/JENK-GAMELIFT']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'legacy/jenkins'], [path: 'legacy/sceptre']]]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'bitbckt-org-wm-bldr', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

                    def commonLib = load "${WORKSPACE}/legacy/jenkins/lib/common.groovy"
                    def awsLib = load "${WORKSPACE}/legacy/jenkins/lib/aws_util.groovy"
                    def secrets = commonLib.getSecrets()

                    wrap([$class: 'VaultBuildWrapper', vaultSecrets: secrets]) {
                        properties([
                                parameters([choice(name: 'SCEPTRE_ACTION', choices: ['--Choose--', 'launch', 'delete', 'validate'], description: 'Action to take'),
                                            string(name: 'GAMELIFT_BUILD_ID', defaultValue: '', description: 'GameLift Build ID: build-........-....-....-....-............', trim: true),
                                            choice(name: 'AWS_REGION', choices: ['us-west-2'], description: 'AWS Region - us-west-2 is default'),
                                            string(name: 'DEPLOYMENT_TARGET', defaultValue: '', description: "legacy destinations: ['int-3', 'int-1', 'int-2', 'prod-1']"),
                                            string(name: 'ORG_ID', defaultValue: '', description: "OrgID: e.g. ['withme', 'withmeqa']"),
                                            choice(name: 'COMPAT_VERSION', choices: ['v1'], description: 'Compatibility Version'),
                                            string(name: 'GAME_SERVER_VERSION', defaultValue: '', description: "Game Server Version"),
                                            string(name: 'DEPLOYMENT_TAG', defaultValue: 'default', description: "Tag to distinguish things like blue, green, default, canary")]),
                                disableConcurrentBuilds()
                        ])


                        def cmd = """
                             cd ${WORKSPACE}/legacy/sceptre/aws
                             export GAMELIFT_BUILD_ID=${GAMELIFT_BUILD_ID}
                             sceptre  --var-file varfiles/fleet-config/${AWS_REGION}/${DEPLOYMENT_TARGET}/values.yaml  ${SCEPTRE_ACTION} ${AWS_REGION}/gamelift-create-fleet"""

                        if (actions_requiring_confirmation.contains(SCEPTRE_ACTION)) {
                            cmd += """ -y
                            """
                        }

                        awsLib.set_aws_creds_and_sh(cmd)
                    }


                }

            }
        }
    }
}
