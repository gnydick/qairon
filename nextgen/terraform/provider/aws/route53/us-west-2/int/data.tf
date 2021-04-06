data "aws_elb" "fooa-lb" {
  name = "a6efe6f02a4f811e9995a0a27fb28875"
}

data "aws_elb" "metrics-lb" {
  name = "a7223c414bfd811e9b2e806be521cd32"
}

data "aws_elb" "jenkins-infra-ng-priv-lb" {
  name = "a01b7e2aeb4b911e98f71027643f8a8c"
}

data "aws_elb" "jenkins-hub-infra-priv-lb" {
  name = "a5f4b2afcb8a911e9b2e806be521cd32"
}


data "aws_elb" "jenkins-agent-lb" {
  name = "a82223780b4b811e98f71027643f8a8c"
}