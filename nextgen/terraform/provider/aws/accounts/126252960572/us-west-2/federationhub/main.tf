provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}


module "xaccount-eks-ci" {
  source = "../../../../../../modules/aws/sa-iam-role"
  cluster_oidc_provider = data.terraform_remote_state.vpc.outputs.cluster_oidc_providers["vpc0"]["infra0"]
  cluster_oidc_provider_arn = data.terraform_remote_state.vpc.outputs.cluster_oidc_provider_arns["vpc0"]["infra0"]
  role_name = "xaccount-eks-ci"
  sa = "system:serviceaccount:default:jenkins"
}

resource "aws_iam_policy" "assume-spoke" {
  name = "federationhub"
  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": [
              "arn:aws:iam::923799771136:role/xaccount-eks-ci",
              "arn:aws:iam::702861675511:role/xaccount-eks-ci",
              "arn:aws:iam::417738154227:role/xaccount-eks-ci",
              "arn:aws:iam::132868707156:role/xaccount-eks-ci"
            ]


        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "assume-spoke" {
  policy_arn = aws_iam_policy.assume-spoke.arn
  role = module.xaccount-eks-ci.role_name
}


resource "aws_iam_policy" "jenkins-sa" {
  name = format("%s.Policy", module.xaccount-eks-ci.role_name)
  policy =<<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Stmt1621879441487",
      "Action": [
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:PutObject"
      ],
      "Effect": "Allow",
      "Resource": [
        "arn:aws:s3:::helm-repo-126252960572.s3-bucket",
        "arn:aws:s3:::helm-repo-126252960572.s3-bucket/stable/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeSpotFleetInstances",
        "ec2:ModifySpotFleetRequest",
        "ec2:CreateTags",
        "ec2:DescribeRegions",
        "ec2:DescribeInstances",
        "ec2:TerminateInstances",
        "ec2:DescribeInstanceStatus",
        "ec2:DescribeSpotFleetRequests"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:DescribeAutoScalingGroups",
        "autoscaling:UpdateAutoScalingGroup"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListInstanceProfiles",
        "iam:ListRoles",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
EOF

}

resource "aws_iam_role_policy_attachment" "jenkins-sa-policy-attachment" {
  policy_arn = aws_iam_policy.jenkins-sa.arn
  role = module.xaccount-eks-ci.role_name
}
