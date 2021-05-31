provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

resource "aws_iam_role" "xaccount-eks-ci" {
  name = "xaccount-eks-ci"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${data.aws_caller_identity.core-lib.account_id}:oidc-provider/${data.terraform_remote_state.vpc.outputs.cluster_oidc_providers["vpc0"]["infra0"]}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${data.terraform_remote_state.vpc.outputs.cluster_oidc_providers["vpc0"]["infra0"]}:sub": "system:serviceaccount:default:jenkins"
        }
      }
    }
  ]
}

EOF
}

resource "aws_iam_policy" "assume-spoke" {
  policy =<<EOF
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
  role = aws_iam_role.xaccount-eks-ci.name
}


resource "aws_iam_policy" "jenkins-sa-s3" {
  name = format("%s.S3Policy", aws_iam_role.xaccount-eks-ci.name)
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
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
    }
  ]
}
EOF

}

resource "aws_iam_role_policy_attachment" "jenkins-sa-policy-attachment" {
  policy_arn = aws_iam_policy.jenkins-sa-s3.arn
  role = aws_iam_role.xaccount-eks-ci.name
}
