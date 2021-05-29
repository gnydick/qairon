package base_jobs

def deployment = params.DEPLOYMENT_ID
def build = params.BUILD_ID
def qairon = load("lib/qairon/main.groovy")

node('helm-installer') {
    container(name: 'helm')
    stage(name: 'parallelize chart releases') {
        checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'main']], extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'nextgen/ops']]], [$class: 'RelativeTargetDirectory', relativeTargetDir: 'bitbucket']], userRemoteConfigs: [[credentialsId: 'jenkins-infra0-bitbucket', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

        build = qairon.get_builds(params.SERVICE_ID)
        print(build)


    }
}
