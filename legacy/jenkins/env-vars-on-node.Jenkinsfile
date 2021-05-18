timestamps {
    podTemplate(name: 'dump-env-vars', label: 'dump-env-vars', yaml: """
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
        node('dump-env-vars') {


            stage('Configure aws account and kubectl config') {
                container('microservice-orchestration') {
                    sh '''
            set -x
            export
        '''
                }
            }
        }
    }
}