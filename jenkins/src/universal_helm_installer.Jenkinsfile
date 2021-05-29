def jobs = [:]

dep_ids = DEPLOYMENTS.split(",")

println(dep_ids)
for (int i = 0; i < dep_ids.size(); i++) {
    def index = i
    def dep_id = dep_ids[index]
    println(dep_ids[index])
    jobs[dep_id] = {
        node('helm-installer') {
            container(name: 'helm') {
                stage(name: 'parallelize helm installations') {

                    def command = $/
                        set -x
                        DEP_DESCRIPTOR=$$(curl -s qairon:5001/api/rest/v1/deployment$/${dep_id})
                        SERVICE_ID=$$(echo $$DEP_DESCRIPTOR | jq -r .service.id)
                        DEP_TARGET=$$(echo $$DEP_DESCRIPTOR | jq -r .deployment_target)
                        DEP_TGT_NAME=$$(echo $$DEP_TARGET | jq -r .name)
                        HELM_CHART=$$(curl -s qairon:5001/api/rest/v1/service$/$$SERVICE_ID |  jq '.defaults|fromjson|.releases.helm')
                        REPO=$$(echo $$HELM_CHART | jq -r .repo)
                        URL=$$(curl -s qairon:5001/api/rest/v1/repo/helm:$$REPO | jq -r .url)
                        ARTIFACT=$$(echo $$HELM_CHART | jq -r .artifact)
                        
                        export AWS_PROFILE=$$(echo $$DEP_TARGET | jq -r '.defaults|fromjson|.spoke_profile')
                        aws eks update-kubeconfig --name $$DEP_TGT_NAME
                        
                        
                        helm repo add $$REPO $$URL
                        helm repo update
                        
                        
                        helm upgrade --install $$ARTIFACT $$REPO$/$$ARTIFACT
                    /$

                    sh script: command
                }
            }
        }
    }
}
parallel(jobs)