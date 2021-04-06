
module "k8s_roles" {
  source = "../../../../../../../../../modules/k8s_roles"
  clustername = "${var.clustername}"
  environment = "${var.environment}"
}

resource "aws_iam_policy" "allowed-to-assume-route53-ng" {
  name = "allowed-to-assume-route53-ng"
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "sts:AssumeRole",
    "Resource": "arn:aws:iam::444444444444:role/ng-external-dns-updater"
  }]
}

EOF
}

resource "aws_iam_role_policy_attachment" "allow-assume-attach" {
  policy_arn = "${aws_iam_policy.allowed-to-assume-route53-ng.arn}"
  role = "prod-infrasvcs-1-stack-NodeInstanceRole-ABSXW6FFT25R"
}