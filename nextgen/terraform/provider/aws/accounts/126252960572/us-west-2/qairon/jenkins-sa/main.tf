resource "aws_iam_role" "jenks-sa" {
  name = "Vpc0Infra0JenkinsSA"
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
    },
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sts.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "jenkins-sa-s3" {

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
      "Resource": "arn:aws:s3:::helm-repo-126252960572.s3-bucket"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "jenkins-sa-policy-attachment" {
  policy_arn = aws_iam_policy.jenkins-sa-s3.arn
  role = aws_iam_role.jenks-sa.name
}