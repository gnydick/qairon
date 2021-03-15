# Sceptre StackConfigs for UPR

In that directory we store all Sceptre StackConfigs for UPR.

## SSH access to the UPR EC2 Instance in the "int-2" environment

Connection to the UPR EC2 Instances is implemented through AWS SystemManager and can be done through your local AWS CLI without any SSH keys, here an example:
Note: For using AWS SSM sessions you will need to have installed "AWS Session Manager Plugin". [Install AWS Session Manager Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

~~~~bash
$ aws ssm describe-instance-information --filters "Key=tag:Name,Values=int-2-upr-cluster-Node"
{
    "InstanceInformationList": [
        {
            "InstanceId": "i-0f6f262f1c76fa3a3",<-------InstanceId is dynamical value and can be changed after UPR instance restart.
            "PingStatus": "Online",
            "LastPingDateTime": 1594997710.356,
            "AgentVersion": "2.3.1319.0",
            "IsLatestVersion": false,
            "PlatformType": "Linux",
            "PlatformName": "Amazon Linux",
            "PlatformVersion": "2",
            "ResourceType": "EC2Instance",
            "IPAddress": "10.132.239.213",
            "ComputerName": "ip-10-132-239-213.us-west-2.compute.internal"
        },
        {
            "InstanceId": "i-031e2536f1e9ca117",<-------InstanceId is dynamical value and can be changed after UPR instance restart.
            "PingStatus": "Online",
            "LastPingDateTime": 1594997690.469,
            "AgentVersion": "2.3.1319.0",
            "IsLatestVersion": false,
            "PlatformType": "Linux",
            "PlatformName": "Amazon Linux",
            "PlatformVersion": "2",
            "ResourceType": "EC2Instance",
            "IPAddress": "10.132.202.203",
            "ComputerName": "ip-10-132-202-203.us-west-2.compute.internal"
        }
    ]
}
$ aws ssm start-session --target i-031e2536f1e9ca117
Starting session with SessionId: build-09832d286e63d69ab
sh-4.2$
~~~~
