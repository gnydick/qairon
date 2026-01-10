#!/usr/bin/env python3
import io
import json
import sys
from pathlib import Path

from qairon_qcli.controllers import QCLIController, PrintingOutputController, StringIOOutputController, \
    IterableOutputController

PROJECT_DIR = Path(__file__)

sys.path.append(
    str(PROJECT_DIR)
)

## Iterable
results = []
ioc = IterableOutputController(results)
qcli = QCLIController(ioc)

# environments
#     for env in ["infra", "prod", "dev", "stg", "int", "local"]:
#         qcli.create({"resource": "environment", "id": env})
#         for row in results:
#             print(row)
#     results.clear()
#
#     for provider_type in ['aws', 'dev']:
#         qcli.create({"resource": "provider_type", "id": provider_type})
#     results.clear()

for provider in ['126252960572']:
    qcli.create({"resource": "provider", "provider_type_id": "aws", "environment_id": "infra", "native_id": provider})
    if type(results) == dict:
        results = [results]
    for row in results:
        data = json.loads(row)
        print(row)
    results.clear()

for region in ['us-west-2']:
    qcli.create({"resource": "region", "provider_id": data['id'], "name": region})
    for row in results:
        print(row)
    results.clear()
# ## availability zones
# ./qairon_qcli/qcli.py zone create infra:aws:126252960572:us-west-2 usw2-az1
# ./qairon_qcli/qcli.py zone create infra:aws:126252960572:us-west-2 usw2-az2
# ./qairon_qcli/qcli.py zone create infra:aws:126252960572:us-west-2 usw2-az3
# ./qairon_qcli/qcli.py zone create infra:aws:126252960572:us-west-2 usw2-az4
# #
# ## partition is a VPC or the like in other vendors
# ./qairon_qcli/qcli.py partition create infra:aws:126252960572:us-west-2 vpc0 -n vpc-074b080f312234a06
#
#
# # records the cidr for our vpc
# ./qairon_qcli/qcli.py network create infra:aws:126252960572:us-west-2:vpc0 default 10.0.0.0/16
#
# # recording all of the subnets that have already been created
# # normally, qairon will create these entries and tell you the x.x.x.x/y
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_nodes1 "10.0.5.0/24" -n "subnet-053d6f76c4be72b99"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_cp3 "10.0.0.48/28" -n "subnet-0166277520e0ac30a"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default rds3 "10.0.9.0/26" -n "subnet-039236e08ed17171c"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default nat_gw0 "10.0.0.64/28" -n "subnet-067603477efb0afe5"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_nodes3 "10.0.7.0/24" -n "subnet-0eedbc8736704de2c"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_cp1 "10.0.0.16/28" -n "subnet-04dd416bc75d0fc23"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_nodes2 "10.0.6.0/24" -n "subnet-0e28eb030895160ef"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default nat_gw3 "10.0.0.112/28" -n "subnet-059e94b56e1ea3417"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default rds0 "10.0.8.64/26" -n "subnet-0cd6b15d33344db25"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_nodes0 "10.0.4.0/24" -n "subnet-064c87babb705d3a0"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_cp2 "10.0.0.32/28" -n "subnet-0758d30cdcad1f1cb"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default nat_gw1 "10.0.0.80/28" -n "subnet-0879dbffa0d102763"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default eks_cp0 "10.0.0.0/28" -n "subnet-0fe20c570e90e1eba"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default rds1 "10.0.8.128/26" -n "subnet-04fe9d32fc0971108"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default rds2 "10.0.8.192/26" -n "subnet-0405562e4ad70c6e8"
# ./qairon_qcli/qcli.py subnet create infra:aws:126252960572:us-west-2:vpc0:default nat_gw2 "10.0.0.96/28" -n "subnet-051316a1151cbc29d"
#
#
# # Artifact tracking
# ./qairon_qcli/qcli.py repo_type create git
# ./qairon_qcli/qcli.py repo_type create ecr
# ./qairon_qcli/qcli.py repo_type create helm
# ./qairon_qcli/qcli.py repo create git 'qairon' 'git@github.com:gnydick/qairon'
# ./qairon_qcli/qcli.py repo create ecr 'qairon' '126252960572.ecr.us-west2.aws.com/qairon'
# ./qairon_qcli/qcli.py repo create ecr 'jenkins' '126252960572.ecr.us-west2.aws.com/jenkins'
# ./qairon_qcli/qcli.py repo create helm bitnami https://charts.bitnami.com/bitnami
# ./qairon_qcli/qcli.py repo create helm qairon 's3://126252960572-helm-repo/stable'
#
#
#
# # Application -> Stack -> Service hierarchy
# ./qairon_qcli/qcli.py application create foobiz
# ./qairon_qcli/qcli.py stack create foobiz cicd
# ./qairon_qcli/qcli.py stack create foobiz automation
# ./qairon_qcli/qcli.py service create foobiz:automation qairon
# ./qairon_qcli/qcli.py service create foobiz:cicd  jenkins -d '{
#    "releases":{
#       "helm":{
#          "repo":"jenkins",
#          "artifact":"jenkins"
#       }
#    }
# }'
#
#
#
# # configuration section
# # default template for gamelift fleet
# export doc=$(cat <<EOF
# {
#   "Type" : "AWS::GameLift::Fleet",
#   "Properties" : {
#       "BuildId" : String,
#       "CertificateConfiguration" : CertificateConfiguration,
#       "Description" : String,
#       "DesiredEC2Instances" : Integer,
#       "EC2InboundPermissions" : [ IpPermission, ... ],
#       "EC2InstanceType" : String,
#       "FleetType" : String,
#       "InstanceRoleARN" : String,
#       "LogPaths" : [ String, ... ],
#       "MaxSize" : Integer,
#       "MetricGroups" : [ String, ... ],
#       "MinSize" : Integer,
#       "Name" : String,
#       "NewGameSessionProtectionPolicy" : String,
#       "PeerVpcAwsAccountId" : String,
#       "PeerVpcId" : String,
#       "ResourceCreationLimitPolicy" : ResourceCreationLimitPolicy,
#       "RuntimeConfiguration" : RuntimeConfiguration,
#       "ScriptId" : String,
#       "ServerLaunchParameters" : String,
#       "ServerLaunchPath" : String
#     }
# }
# EOF
# )
#
# # language label for a configuration
# ./qairon_qcli/qcli.py language create json
#
# # creating a template marked as json with the contents from above
# ./qairon_qcli/qcli.py config_template create json cfn-gamelift-fleet   1 -c "$doc"
#
# # first, creating deployment target types
# ./qairon_qcli/qcli.py deployment_target_type create eks
#
#
#
# # the deployment targets themselves
# ./qairon_qcli/qcli.py deployment_target create eks infra:aws:126252960572:us-west-2:vpc0 infra0
#
#
#
#
# # then the actual deployments linking deployment target and service
# ./qairon_qcli/qcli.py deployment create foobiz:automation:qairon infra:aws:126252960572:us-west-2:vpc0:eks:infra0
#
# # CICD data
# # builds -- immutable blobs from build pipeline
# ./qairon_qcli/qcli.py build create foobiz:automation:qairon 422 v0.1
# ./qairon_qcli/qcli.py build create foobiz:automation:qairon 564 v0.2
# ./qairon_qcli/qcli.py build create foobiz:cicd:jenkins 456 v1.0
# ./qairon_qcli/qcli.py build create foobiz:cicd:jenkins 567 v1.1
#
# ./qairon_qcli/qcli.py build_artifact create foobiz:automation:qairon:422 git:qairon ecr:qairon docker_image foobarbaz
#
# # releases -- installation instructions bundled with any appropriate config for that deployment
# # e.g. -- helm chart tar ball with additional configuration that is deployment target specific bundled in
# ./qairon_qcli/qcli.py release create foobiz:automation:qairon:422 infra:aws:126252960572:us-west-2:vpc0:eks:infra0:bin0:foobiz:automation:qairon:default 1023
# ./qairon_qcli/qcli.py release create foobiz:automation:qairon:564 infra:aws:126252960572:us-west-2:vpc0:eks:infra0:bin0:foobiz:automation:qairon:default 1104
# ./qairon_qcli/qcli.py release_artifact create infra:aws:126252960572:us-west-2:vpc0:eks:infra0:bin0:foobiz:automation:qairon:default:1104 ecr:qairon helm:qairon helm_chart foobarbaz
