data "aws_elb" "metrics" {
  name = "af8ee8e56b93611e9b5540617fffd7a0"
}

data "aws_elb" "fooa" {
  name = "aeb4b77c1bfe211e998df063a6466dab"
}

data "aws_vpc" "hosted_zone_vpc" {
  cidr_block = "172.20.0.0/16"
  tags = {
    "kubernetes.io/cluster/stage.foo.k8s.local" = "owned"
  }
}