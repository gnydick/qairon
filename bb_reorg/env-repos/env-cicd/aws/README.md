# Cluster initiation and adding worker nodes to it.

* Elements
     * CICD cluster revive
     * CLI tools
     * Cluster initiation
     * Adding new Node Stack to cluster


## CICD cluster revive

* Cluster specs:
     * EKS cluster version: 1.15
     * Region: us-west-2
     * AZ's: us-west-2a, us-west-2b, us-west-2c
     * Subnets: 3 Public for NatGateway and 3 Private for NodeGroup's
     * Nodes: Three t3.large nodes (in each Private subnet)
     * Node AMI: ami-065418523a44331e5

![Alt text](https://d1.awsstatic.com/partner-network/QuickStart/datasheets/amazon-eks-on-aws-architecture-diagram.7fdf06380021e6dc7c622d298d99e3c1154163bc.png)

## CLI tools

*  CLI tools that you will need to deploy cluster all that tools contained in [ ego-cicd-devenv ](https://bitbucket.org/imvu/ego-cicd-devenv/src/master/)
     * AWS CLI
     * aws-iam-authenticator
     * kubectl
     * Sceptre

## Cluster initiation

At first make sure that you "build" user:

```bash
aws sts get-caller-identity --output text
```

Creating key pare:

```bash
aws ec2 create-key-pair --key-name kubernetes-cicd-key-pair
```

Make sure that you in `./cloudformation-cicd` directory!

```bash
$ pwd
/your/pc/path/to/repo/env-cicd/cloudformation-cicd
```

Now we can run cloudformation template:

```bash
aws cloudformation create-stack --region us-west-2 --stack-name env-cicd --template-body file://cicd-cloudformation-vpc-eks.yaml --capabilities CAPABILITY_IAM
```

You can check stack status on AWS Web Console CloudFormation page.
When stack status will be "CREATE_COMPLETE"
You need to generate `.kubeconfig` in your workstation for communication with cluster:

```bash
aws eks --region us-west-2 update-kubeconfig --name cicd
```

Check your `.kubeconfig` and cluster status by command:

```bash
kubectl get svc
```

If you get something similar to:

```bash
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   X.X.X.X      <none>        443/TCP   Xm
```

If output don't look like in the example, you need to check your kubectl context!
If output like an example...You are on the right way!

Next step is adding `cicd-util` Node Stack that created with cluster by `cicd-cloudformation-template.yaml`
For that, you will need `aws-auth-cm.yaml` file in `./cloudformation-cicd` repo directory and NodeInstanceRole ARN.

NodeInstanceRole ARN you will find in CloudFormation Stack "env-cicd" Output.
For adding node stack that created with `./cloudformation-cicd` template just run three CLI commands:

```bash
export EKS_WORKER_ROLE=paste_ARN_here
sed -i -e "s#<ARN of instance role (not instance profile)>#${EKS_WORKER_ROLE}#g" ./aws-auth-cm.yaml
kubectl apply -f aws-auth-cm.yaml
```

*Don't forget to update `aws-auth-cm.yaml` in that repository with commit "Update latest state of KubeConfig"*

And now we can watch how WorkerNodes will be added to kubernetes cluster:

```bash
kubectl get nodes --watch
```

When your Nodes get "ready" status. You can start working with cluster by `kubectl` tool.

## Adding new Node Stack to cluster

Creating new Node Stack with Scepter (Check Parameters in `~/env-cicd/aws/config/util-tier/nodes.yaml && cicd-node-iam-policy.yaml` before using it):

```bash
sceptre create util-tier/nodes.yaml -y && sceptre create util-tier/cicd-node-iam-policy.yaml -y
```

When stack status will be `CREATE_COMPLETE`
We need to connect that Node Stack to cluster masters.
For that we will need `aws-auth-cm.yaml` and NodeInstanceRole ARN that you can find in output of your previously deployed CloudFormation stack.
Open `aws-auth-cm.yaml` with text editor and paste that part to the end of file.
```
- rolearn: < ARN of instance role>
  username: system:node:{{EC2PrivateDNSName}}
  groups:
    - system:bootstrappers
    - system:nodes
```
Don't forget to change `< ARN of instance role>` to your NodeInstanceRole ARN.
Save `aws-auth-cm.yaml` and apply it by:
```bash
kubectl apply -f aws-auth-cm.yaml
```
The last step is to update `aws-auth-cm.yaml` with your changes in this repo with commit "Update latest state of KubeConfig"
