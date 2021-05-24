resource "aws_iam_role" "jenks-sa" {
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "${var.cluster_oidc_provider_arn}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${var.cluster_oidc_provider}:sub": "system:serviceaccount:default:jenkins"
        }
      }
    }
  ]
}
EOF
}

