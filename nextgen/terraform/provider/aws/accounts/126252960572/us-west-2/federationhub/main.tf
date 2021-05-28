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
          "${data.terraform_remote_state.vpc.outputs.cluster_oidc_providers["vpc0"]["infra0"]}:sub": "system:serviceaccount:ci-namespace:ci-serviceaccount"
        }
      }
    }
  ]
}

EOF
}