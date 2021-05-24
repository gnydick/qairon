import org.jenkinsci.plugins.workflow.cps.ParamsVariable
params = getParams()

def ENV_ID = params.ENVIRONMENT
def DEP_TARGET_ID = params.DEPLOYMENT_TARGET
def DEP_ID = params.DEPLOYMENT
def label = "jenkins"
DEP_TARGET_ID = 'stage_ng-stage1-us-west-2-eks_k8s'

podTemplate(cloud: 'stage_ng-stage1-us-west-2-eks_k8s', inheritFrom: 'jenkins-builder-ng-stage1', instanceCap: 0, namespace: 'infra', nodeSelector: '', podRetention: always(), serviceAccount: '', workspaceVolume: emptyDirWorkspaceVolume(false), yaml: '') {


    node($DEP_TARGET_ID) {
        def myRepo = checkout scm
        def gitCommit = myRepo.GIT_COMMIT
        def gitBranch = myRepo.GIT_BRANCH
        def shortGitCommit = "${gitCommit[0..10]}"
        def previousGitCommit = sh(script: "git rev-parse ${gitCommit}~", returnStdout: true)




        stage('Run kubectl') {
            container('kubectl') {
                sh "kubectl get pods"
            }
        }
        stage('Run helm') {
            container('helm') {
                sh "helm list"
            }
        }
    }
}