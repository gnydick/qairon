# README

Directory with Scepter Project that describes the production environment.
Before starting you will need to install custom Sceptre hook and resolver.

([Confluence page about using Scepter](https://confluence.corp.imvu.com/display/EGO/Setting+Up+AWS+CloudFormation+Stacks+for+Production), [Scepter official documentation](https://sceptre.cloudreach.com/))

## Base "network" layer

Network layer StackSet include:

- 1xVPC
- 1xInternetGateway
- 3xPublicSubnets
- 3xPrivateSubnets
- 3xNATgateways
- 3xEIP
- 1xPublicRouteTable
- 3xPublicSubnetRouteTableAssociation
- 3xPrivateSubnetRouteTable
- 3xPrivateSubnetRouteTableAssociation

**Deploy "network" layer StackSet:**

1. Change directory to root Sceptre Project directory

    ```$ cd /home/$USER/env-prod-1/aws```

2. Deploy `network` Sceptre StackSet:

    ```$ sceptre create us-west-2/network```

## EKS control plane deployment

EKS StackSet include:

- 1xEKS
- 1xClusterRoleIAM
- 1xControlPlaneSecurityGroup

**Deploy "EKS" StackSet:**

1. Change directory to root Sceptre Project directory

    ```$ cd /home/$USER/env-prod-1/aws```

2. Deploy `eks` Sceptre StackSet:

    ```$ sceptre create us-west-2/eks```

## Bastion hosts deployment

Bastion StackSet include:

- 2xBastionHosts.
- 1xIAM Role.
- 1x AWS CloudWatch LogGroup for collecting startup logs.

Bastion hosts (EC2 instance) will be deployed into Public Subnets (1 Instance per-one AZ) without opened network ports or attached EC2 Keys.
Access to TTY to that instances implemented trough AWS Systems Manager _Session Manager_.

**Deploy "Bastion" and connet to it:**

1. Change directory to root Sceptre Project directory

    ```$ cd /home/$USER/env-prod-1/aws```

2. Deploy `bastion` Sceptre StackSet:

    ```$ sceptre create us-west-2/bastion```

3. If CF Stack created with success you can check that bastion is available in AWS Systems Manager.

    ```$ aws ssm describe-instance-information```

   List bastion instances ID's for connection trough AWS Systems Manager _Session Manager_.

    ```$ aws ssm describe-instance-information```

4. [Install the Session Manager Plugin](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

5. Connect to bastion TTY trough AWS Systems Manager _Session Manager_

    ```$ aws ssm start-session --target <INSTANCE_ID> --document-name AWS-StartInteractiveCommand --parameters command="bash -l"```

6. Configure `ssm-user` bastion environment:

    ```configure_env```

`configure_env` is alias (in `.bashrc`) to bash script that will create kubectl config file, configure local docker, login to ECR repo etc.

**Note: `aws-ssm` user is a temporary user created by AWS SSM only for a one session.**

### Who do I talk to

- mklipikov@imvu.com
