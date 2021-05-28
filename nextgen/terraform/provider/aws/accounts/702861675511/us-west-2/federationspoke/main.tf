provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

resource "aws_iam_role" "xaccount-eks-ci-spoke" {
  name = "xaccount-eks-ci"
  assume_role_policy = <<EOF
{
   "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::126252960572:role/xaccount-eks-ci"
      },
      "Action": "sts:AssumeRole",
      "Condition": {}
    }
  ]
}

EOF
}

resource "aws_iam_policy" "xaccount-eks-ci-spoke"{
  policy =<<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "eks:DescribeCluster",
                "eks:ListClusters"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "xaccount-eks-ci-spoke" {
  policy_arn = aws_iam_policy.xaccount-eks-ci-spoke.arn
  role = aws_iam_role.xaccount-eks-ci-spoke.name
}