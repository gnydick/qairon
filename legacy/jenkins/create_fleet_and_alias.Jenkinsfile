def run_sceptre = { params ->
    print "Hello"
}


node('master') {


    stage('Launch Node') {
        checkout changelog: false, poll: false, scm: [$class: 'GitSCM', branches: [[name: 'features/JENK-GAMELIFT']], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'SparseCheckoutPaths', sparseCheckoutPaths: [[path: 'legacy/jenkins']]]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'bitbckt-org-wm-bldr', url: 'git@bitbucket.org:imvu/withme-ops.git']]]

        def commonLib = load("${WORKSPACE}/legacy/jenkins/lib/common.groovy")
        println(commonLib)
        commonLib.node_with_secrets('test', 'test', 'microservice-orchestration', run_sceptre("foo"))
    }
}

