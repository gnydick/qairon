def common = load('lib/common.groovy')

def run_sceptre(params) {

    sh '''
        ls $WORKSPACE
    '''
}

common.node_with_secrets('test', 'microservice-orchestration', run_sceptre())