resource "aws_iam_role" "cluster_users_role" {
  name               = "${var.cluster_name}.k8s_users"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::966494614521:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

}

resource "aws_iam_policy" "cluster_users_policy" {
  name   = "assume-${var.cluster_name}-k8s_users"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
      {
          "Effect": "Allow",
          "Action": "sts:AssumeRole",
          "Resource": "${aws_iam_role.cluster_users_role.arn}"
      }
  ]
}
EOF

}

resource "aws_iam_policy" "cluster_operations" {
  name   = "${var.cluster_name}-allowed_ops"
  policy = <<EOF
{
"Version": "2012-10-17",
"Statement": [
  {
    "Sid": "Stmt1553719559408",
    "Action": "eks:*",
    "Effect": "Allow",
    "Resource": "${var.cluster_arn}"
  }
]
}
EOF

}

resource "aws_iam_group" "cluster_users_group" {
  name = "${var.cluster_name}-k8s_users"
}

resource "aws_iam_role_policy_attachment" "cluster_users_role_policy_attachment" {
  policy_arn = aws_iam_policy.cluster_users_policy.arn
  role       = aws_iam_role.cluster_users_role.name
}

resource "aws_iam_role_policy_attachment" "cluster_ops_role_policy_attachment" {
  policy_arn = aws_iam_policy.cluster_operations.arn
  role       = aws_iam_role.cluster_users_role.name
  depends_on = [aws_iam_policy.cluster_operations]
}

resource "aws_iam_group_policy_attachment" "cluster_users_group_policy_attachment" {
  group      = aws_iam_group.cluster_users_group.name
  policy_arn = aws_iam_policy.cluster_users_policy.arn
}

