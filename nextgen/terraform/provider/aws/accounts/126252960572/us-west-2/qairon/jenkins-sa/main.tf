module "sa-iam-role" {
  source = "../../../../../../../modules/aws/sa-iam-role"
  cluster_oidc_provider = var.cluster_oidc_provider
  cluster_oidc_provider_arn = var.cluster_oidc_provider_arn
  role_name = "Vpc0Infra0JenkinsSA"
  sa = "system:serviceaccount:default:jenkins"
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
  role = "Vpc0Infra0JenkinsSA"
}
