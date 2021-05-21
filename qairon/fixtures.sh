export SQLALCHEMY_DATABASE_URI=postgresql://qairon:qairon@localhost/qairon
./qcli pop_type create aws
./qcli pop_type create dev
./qcli pop create aws 661959915760
./qcli pop create dev laptop
./qcli region create aws:661959915760 us-west-2
./qcli region create dev:laptop here
./qcli zone create aws:661959915760:us-west-2 usw2-az1
./qcli zone create aws:661959915760:us-west-2 usw2-az2
./qcli zone create aws:661959915760:us-west-2 usw2-az3
./qcli partition create aws:661959915760:us-west-2 rshaham_web_server -n vpc-144db37f
./qcli partition create dev:laptop:here default
./qcli network create aws:661959915760:us-west-2:rshaham_web_server default 172.31.0.0/16
./qcli subnet create aws:661959915760:us-west-2:rshaham_web_server:default subnet-5659de1a 172.31.32.0/20
./qcli subnet create aws:661959915760:us-west-2:rshaham_web_server:default subnet-32520d48 172.31.16.0/20
./qcli subnet create aws:661959915760:us-west-2:rshaham_web_server:default subnet-72846519 172.31.0.0/20
./qcli application create withme
./qcli application create poc
./qcli stack create withme services
./qcli stack create poc automation
./qcli repo_type create ecr
./qcli repo_type create helm
./qcli repo create ecr 'game-server-manager.image' '661959915760.ecr.us-west2.aws.com/game-server-manager'
./qcli repo create ecr 'web_server' '661959915760.ecr.us-west2.aws.com/web_server'
./qcli repo create helm bitnami https://charts.bitnami.com/bitnami
./qcli service create withme:services ecr:game-server-manager.image game_server_manager
./qcli service create poc:automation ecr:web_server web_server2 -d '{
   "releases":{
      "helm":{
         "repo":"bitnami",
         "artifact":"nginx"
      }
   }
}'
echo int-1 int-2 prod perf-1 cicd local | xargs -n 1 ./qcli environment create
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
./qcli build create poc:automation:web_server 456 v1.0
./qcli build create poc:automation:web_server 567 v1.1
./qcli deployment create poc:automation:web_server dev:laptop:here:default:local:minikube:vbox
./qcli release create poc:automation:web_server:v1.0:456 dev:laptop:here:default:local:minikube:vbox:poc:automation:web_server:default 789