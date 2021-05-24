def label = "worker-${UUID.randomUUID().toString()}"

podTemplate(label: label, containers: [
        containerTemplate(name: 'kubectl', image: '966494614521.dkr.ecr.us-west-2.amazonaws.com/kubectl:0.0', command: 'cat', ttyEnabled: true),
        containerTemplate(name: 'helm', image: '966494614521.dkr.ecr.us-west-2.amazonaws.com/helm:0.0', command: 'cat', ttyEnabled: true)
],
        volumes: [
                hostPathVolume(mountPath: '/var/run/docker.sock', hostPath: '/var/run/docker.sock')
        ]) {
    node(label) {
        def myRepo = checkout scm
        def gitCommit = myRepo.GIT_COMMIT
        def gitBranch = myRepo.GIT_BRANCH
        def shortGitCommit = "${gitCommit[0..10]}"
        def previousGitCommit = sh(script: "git rev-parse ${gitCommit}~", returnStdout: true)


        stage('Build') {
            sh "npm install"
        }
        stage('Create Docker images') {
            sh """
        \$(aws ecr get-login --no-include-email --region=us-west2-2)
        docker build -t namespace/my-image:${gitCommit} .
        docker push namespace/my-image:${gitCommit}
        """
        }
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