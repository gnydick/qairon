data "aws_elb" "metrics" {
  name = "ad61da6d0c0f711e9831502275135a90"
}

data "aws_elb_hosted_zone_id" "elb_zone" {
  region = "${var.region}"
}

data "aws_vpc" "hosted_zone_vpc" {
  cidr_block = "172.20.0.0/16"
  tags = {
    "kubernetes.io/cluster/qa.foo.k8s.local" = "owned"
  }
}