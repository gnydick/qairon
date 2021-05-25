data "aws_iam_policy_document" "jenkins-sa-assume-role-policy" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    condition {
      test     = "StringEquals"
      variable = "${var.cluster_oidc_provider}:sub"
      values   = ["system:serviceaccount:default:jenkins"]
    }

    principals {
      identifiers = [var.cluster_oidc_provider_arn]
      type        = "Federated"
    }
  }
}

resource "aws_iam_role" "jenkins-sa" {
  assume_role_policy = data.aws_iam_policy_document.jenkins-sa-assume-role-policy.json
  name               = "Vpc0Infra0JenkinsSA"

}

resource "aws_iam_policy" "jenkins-sa-s3" {
  name = "Vpc0Infra0JenkinsSAPolicy"
  policy = <<EOF
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
    }
  ]
}
EOF

}

resource "aws_iam_role_policy_attachment" "jenkins-sa-policy-attachment" {
  policy_arn = aws_iam_policy.jenkins-sa-s3.arn
  role = aws_iam_role.jenkins-sa.name
}
