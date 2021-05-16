package base_jobs

import groovy.json.JsonSlurper

def helm_install(deployment_descriptor) {

    container(name: 'helm') {
        stage(name: 'parallelize helm installations') {

            // feed in release id's to download helm archives, then loop over the shell command

            sh '''
            set -x
            
            HELM_SOURCE=$(curl -s qairon:5001/api/rest/v1/service/${SERVICE_ID} | jq -r  '.defaults | fromjson | .releases.helm')
            REPO=$(echo $HELM_SOURCE | jq -r .repo)
            URL=$(curl -s qairon:5001/api/rest/v1/repo/helm:${REPO} | jq -r .url)
            ARTIFACT=$(echo ${HELM_SOURCE} | jq -r .artifact)
            echo "ideally we would download a specifically packaged helm chart based on the build rolled into a release archive"
            echo "also, we would use the specified deployment target from the specified deployment"
            helm repo add $REPO $URL
            helm repo update
            helm upgrade --install $ARTIFACT $REPO/$ARTIFACT
        '''
        }
    }
}