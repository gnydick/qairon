resource "aws_iam_role" "k8s_users" {
  name = "k8s_users-${var.environment}-${var.clustername}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

EOF

}