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
                        REL_BUILD_NUM=$$(echo $$DEP_DESCRIPTOR | jq -r .current_release.build_num)
                        SERVICE_ID=$$(echo $$DEP_DESCRIPTOR | jq -r .service.id)
                        SERVICE_NAME=$$(echo $$DEP_DESCRIPTOR | jq -r .service.name)
                        DEP_TARGET=$$(echo $$DEP_DESCRIPTOR | jq -r .deployment_target)
                        DEP_TGT_NAME=$$(echo $$DEP_TARGET | jq -r .name)
                        HELM_CHART=$$(curl -s qairon:5001/api/rest/v1/service$/$$SERVICE_ID |  jq '.defaults|fromjson|.releases.helm')
                        REPO=$$(echo $$HELM_CHART | jq -r .repo)
                        URL=$$(curl -s qairon:5001/api/rest/v1/repo/helm:$$REPO | jq -r .url)
                        
                        
                        aws s3 cp $$URL$/${dep_id}$/$$SERVICE_NAME-$$REL_BUILD_NUM.tgz $$SERVICE_NAME-$$REL_BUILD_NUM.tgz 

                        export AWS_PROFILE=$$(echo $$DEP_TARGET | jq -r '.defaults|fromjson|.spoke_profile')
                        aws eks update-kubeconfig --name $$DEP_TGT_NAME
                  
                        helm upgrade --install $$SERVICE_NAME .$/$$SERVICE_NAME-$$REL_BUILD_NUM.tgz
                    /$

                    sh script: command
                }
            }
        }
    }
}
parallel(jobs)