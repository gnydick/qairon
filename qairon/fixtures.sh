## provider type is like cloud vendor
#./qcli provider_type create aws
#
## dev as a provider type means somewhere in our dev env, could be laptop
#./qcli provider_type create dev
#
## creates aws account
#./qcli provider create aws 126252960572 infra

# creates a dev provider to represent laptop
#./qcli provider create dev 0000000000000 laptop

# self explanatory
./qcli region create aws:126252960572 us-west-2

# just need a place holder region for local development
./qcli region create dev:0000000000000 here

# availability zones
./qcli zone create aws:126252960572:us-west-2 usw2-az1
./qcli zone create aws:126252960572:us-west-2 usw2-az2
./qcli zone create aws:126252960572:us-west-2 usw2-az3
./qcli zone create aws:126252960572:us-west-2 usw2-az4

# partition is a VPC or the like in other vendors
./qcli partition create aws:126252960572:us-west-2 vpc0 -n vpc-074b080f312234a06

# again, placeholder for local development
./qcli partition create dev:0000000000000:here default

# records the cidr for our vpc
./qcli network create aws:126252960572:us-west-2:vpc0 default 10.0.0.0/16

# recording all of the subnets that have already been created
# normally, qairon will create these entries and tell you the x.x.x.x/y
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes1 "10.0.5.0/24" -n "subnet-053d6f76c4be72b99"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp3 "10.0.0.48/28" -n "subnet-0166277520e0ac30a"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds3 "10.0.9.0/26" -n "subnet-039236e08ed17171c"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw0 "10.0.0.64/28" -n "subnet-067603477efb0afe5"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes3 "10.0.7.0/24" -n "subnet-0eedbc8736704de2c"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp1 "10.0.0.16/28" -n "subnet-04dd416bc75d0fc23"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes2 "10.0.6.0/24" -n "subnet-0e28eb030895160ef"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw3 "10.0.0.112/28" -n "subnet-059e94b56e1ea3417"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds0 "10.0.8.64/26" -n "subnet-0cd6b15d33344db25"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_nodes0 "10.0.4.0/24" -n "subnet-064c87babb705d3a0"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp2 "10.0.0.32/28" -n "subnet-0758d30cdcad1f1cb"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw1 "10.0.0.80/28" -n "subnet-0879dbffa0d102763"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default eks_cp0 "10.0.0.0/28" -n "subnet-0fe20c570e90e1eba"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds1 "10.0.8.128/26" -n "subnet-04fe9d32fc0971108"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default rds2 "10.0.8.192/26" -n "subnet-0405562e4ad70c6e8"
./qcli subnet create aws:126252960572:us-west-2:vpc0:default nat_gw2 "10.0.0.96/28" -n "subnet-051316a1151cbc29d"


# Artifact tracking
./qcli repo_type create ecr
./qcli repo_type create helm
./qcli repo create ecr 'qairon' '126252960572.ecr.us-west2.aws.com/qairon'
./qcli repo create ecr 'jenkins' '126252960572.ecr.us-west2.aws.com/jenkins'
./qcli repo create helm bitnami https://charts.bitnami.com/bitnami



# Application -> Stack -> Service hierarchy
./qcli application create withme
./qcli stack create withme cicd
./qcli stack create withme automation
./qcli service create withme:automation qairon
./qcli service create withme:cicd  jenkins -d '{
   "releases":{
      "helm":{
         "repo":"jenkins",
         "artifact":"jenkins"
      }
   }
}'

# environments
for ENV in  infra prod dev stg int local ; do  ./qcli environment create $ENV ; done

# configuration sectino
# default template for gamelift fleet
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

# language label for a configuration
./qcli language create json

# creating template type
./qcli config_template_type create cfn-gamelift-fleet

# creating a template marked as json with the contents from above
./qcli config_template create cfn-gamelift-fleet json  1 -c "$doc"

# first, creating deployment target types
./qcli deployment_target_type create eks

# minikube for local development
./qcli deployment_target_type create minikube


# the deployment targets themselves
./qcli deployment_target create minikube dev:0000000000000:here:default local vbox
./qcli deployment_target create eks aws:126252960572:us-west-2:vpc0 infra infra0


# then the actual deployments linking deployment target and service
./qcli deployment create withme:cicd:jenkins dev:0000000000000:here:default:local:minikube:vbox
./qcli deployment create withme:automation:qairon aws:126252960572:us-west-2:vpc0:infra:eks:infra0

# CICD data
# builds -- immutable blobs from build pipeline
./qcli build create withme:automation:qairon 422 v0.1
./qcli build create withme:automation:qairon 564 v0.2
./qcli build create withme:cicd:jenkins 456 v1.0
./qcli build create withme:cicd:jenkins 567 v1.1


# releases -- installation instructions bundled with any appropriate config for that deployment
# e.g. -- helm chart tar ball with additional configuration that is deployment target specific bundled in
./qcli release create withme:cicd:jenkins:456 dev:laptop:here:default:local:minikube:vbox:withme:cicd:jenkins:default 789
./qcli release create withme:automation:qairon:422 aws:126252960572:us-west-2:vpc0:infra:eks:infra0:withme:automation:qairon:default 1023
./qcli release create withme:automation:qairon:564 aws:126252960572:us-west-2:vpc0:infra:eks:infra0:withme:automation:qairon:default 1104