export SQLALCHEMY_DATABASE_URI=postgresql://qairon:qairon@localhost:5433/qairon
#./qcli pop_type create aws
#./qcli pop_type create dev
#./qcli pop create aws 126252960572
#./qcli pop create dev laptop
#./qcli region create aws:126252960572 us-west-2
#./qcli region create dev:laptop here
#./qcli zone create aws:126252960572:us-west-2 usw2-az1
#./qcli zone create aws:126252960572:us-west-2 usw2-az2
#./qcli zone create aws:126252960572:us-west-2 usw2-az3
#./qcli zone create aws:126252960572:us-west-2 usw2-az4
#./qcli partition create aws:126252960572:us-west-2 vpc0 -n vpc-074b080f312234a06
#./qcli partition create dev:laptop:here default
#./qcli network create aws:126252960572:us-west-2:vpc0 default 10.0.0.0/16
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes1 "10.0.5.0/24" -n "subnet-053d6f76c4be72b99"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp3 "10.0.0.48/28" -n "subnet-0166277520e0ac30a"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds3 "10.0.9.0/26" -n "subnet-039236e08ed17171c"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw0 "10.0.0.64/28" -n "subnet-067603477efb0afe5"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes3 "10.0.7.0/24" -n "subnet-0eedbc8736704de2c"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp1 "10.0.0.16/28" -n "subnet-04dd416bc75d0fc23"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes2 "10.0.6.0/24" -n "subnet-0e28eb030895160ef"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw3 "10.0.0.112/28" -n "subnet-059e94b56e1ea3417"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds0 "10.0.8.64/26" -n "subnet-0cd6b15d33344db25"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes0 "10.0.4.0/24" -n "subnet-064c87babb705d3a0"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp2 "10.0.0.32/28" -n "subnet-0758d30cdcad1f1cb"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw1 "10.0.0.80/28" -n "subnet-0879dbffa0d102763"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp0 "10.0.0.0/28" -n "subnet-0fe20c570e90e1eba"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds1 "10.0.8.128/26" -n "subnet-04fe9d32fc0971108"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds2 "10.0.8.192/26" -n "subnet-0405562e4ad70c6e8"
#./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw2 "10.0.0.96/28" -n "subnet-051316a1151cbc29d"

#./qcli application create withme
#./qcli stack create withme cicd
#./qcli stack create withme automation
#./qcli repo_type create ecr
#./qcli repo_type create helm
#./qcli repo create ecr 'qairon.image' '126252960572.ecr.us-west2.aws.com/game-server-manager'
#./qcli repo create ecr 'jenkins.image' '126252960572.ecr.us-west2.aws.com/jenkins.image'
#./qcli repo create helm bitnami https://charts.bitnami.com/bitnami
#./qcli service create withme:automation ecr:qairon.image qairon
#./qcli service create withme:cicd ecr:jenkins.image jenkins -d '{
#   "releases":{
#      "helm":{
#         "repo":"jenkins",
#         "artifact":"jenkins"
#      }
#   }
#}'
#for ENV in  infra prod dev stg int local ; do  ./qcli environment create $ENV ; done
export doc=$(cat <<EOF
{
  "Type" : "AWS::GameLift::Fleet",
  "Properties" : {
      "BuildId" : String,
      "CertificateConfiguration" : CertificateConfiguration,
      "Description" : String,
      "DesiredEC2Instances" : Integer,
      "EC2InboundPermissions" : [ IpPermission, ... ],
      "EC2InstanceType" : String,
      "FleetType" : String,
      "InstanceRoleARN" : String,
      "LogPaths" : [ String, ... ],
      "MaxSize" : Integer,
      "MetricGroups" : [ String, ... ],
      "MinSize" : Integer,
      "Name" : String,
      "NewGameSessionProtectionPolicy" : String,
      "PeerVpcAwsAccountId" : String,
      "PeerVpcId" : String,
      "ResourceCreationLimitPolicy" : ResourceCreationLimitPolicy,
      "RuntimeConfiguration" : RuntimeConfiguration,
      "ScriptId" : String,
      "ServerLaunchParameters" : String,
      "ServerLaunchPath" : String
    }
}
EOF
)
./qcli language create json
./qcli config_template_type create cfn-gamelift-fleet
./qcli config_template create cfn-gamelift-fleet json  1 -c "$doc"
./qcli deployment_target_type create eks
./qcli deployment_target_type create minikube
./qcli deployment_target create minikube dev:laptop:here:default local vbox
./qcli deployment_target create eks aws:126252960572:us-west-2:vpc0 infra infra0
./qcli deployment create withme:cicd:jenkins dev:laptop:here:default:local:minikube:vbox
./qcli deployment create withme:automation:qairon aws:126252960572:us-west-2:vpc0:infra:eks:infra0
./qcli build create withme:automation:qairon 422 v0.1
./qcli build create withme:automation:qairon 564 v0.2
./qcli build create withme:cicd:jenkins 456 v1.0
./qcli build create withme:cicd:jenkins 567 v1.1
./qcli release create withme:cicd:jenkins:v1.0:456 dev:laptop:here:default:local:minikube:vbox:withme:cicd:jenkins:default 789
./qcli release create withme:automation:qairon:v0.1:422 aws:126252960572:us-west-2:vpc0:infra:eks:infra0:withme:automation:qairon:default 1023
./qcli release create withme:automation:qairon:v0.2:564 aws:126252960572:us-west-2:vpc0:infra:eks:infra0:withme:automation:qairon:default 1104