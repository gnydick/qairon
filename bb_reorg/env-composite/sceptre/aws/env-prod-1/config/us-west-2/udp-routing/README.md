# Sceptre StackConfigs for UPR

In that directory we store all Sceptre StackConfigs for UPR.

## SSH access to the UPR EC2 Instance in the "prod-1" environment

Connection to the UPR EC2 Instances is implemented through AWS SystemManager and can be done through your local AWS CLI without any SSH keys, here an example:
Note: For using AWS SSM sessions you will need to have installed "AWS Session Manager Plugin". [Install AWS Session Manager Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

~~~~bash
$ aws ssm describe-instance-information --filters "Key=tag:Name,Values=prod-1-upr-cluster-Node"
{
    "InstanceInformationList": [
        {
            "InstanceId": "i-0b59e40daaf747dc4",
            "PingStatus": "Online",
            "LastPingDateTime": 1603358827.531,
            "AgentVersion": "2.3.714.0",
            "IsLatestVersion": false,
            "PlatformType": "Linux",
            "PlatformName": "Amazon Linux",
            "PlatformVersion": "2",
            "ResourceType": "EC2Instance",
            "IPAddress": "10.132.207.198",
            "ComputerName": "ip-10-132-207-198.us-west-2.compute.internal"
        },
        {
            "InstanceId": "i-09a9fb6320d04ab57",
            "PingStatus": "Online",
            "LastPingDateTime": 1603358888.308,
            "AgentVersion": "2.3.714.0",
            "IsLatestVersion": false,
            "PlatformType": "Linux",
            "PlatformName": "Amazon Linux",
            "PlatformVersion": "2",
            "ResourceType": "EC2Instance",
            "IPAddress": "10.132.218.132",
            "ComputerName": "ip-10-132-218-132.us-west-2.compute.internal"
        },
        {
            "InstanceId": "i-015be6c35fb003189",
            "PingStatus": "Online",
            "LastPingDateTime": 1603358831.652,
            "AgentVersion": "2.3.714.0",
            "IsLatestVersion": false,
            "PlatformType": "Linux",
            "PlatformName": "Amazon Linux",
            "PlatformVersion": "2",
            "ResourceType": "EC2Instance",
            "IPAddress": "10.132.225.119",
            "ComputerName": "ip-10-132-225-119.us-west-2.compute.internal"
        }
    ]
}

$ aws ssm start-session --target i-0b59e40daaf747dc4
Starting session with SessionId: build-09832d286e63d69ab
sh-4.2$
~~~~
