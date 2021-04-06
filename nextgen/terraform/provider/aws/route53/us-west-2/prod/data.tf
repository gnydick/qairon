data "aws_elb" "metrics" {
  name = "aa7318e41c01811e9883f024d7d42b77"
}

data "aws_elb" "fooa" {
  name = "a814cdf21c01a11e9883f024d7d42b77"
}

data "aws_vpc" "hosted_zone_vpc" {
  cidr_block = "172.20.0.0/16"
  tags = {
    "kubernetes.io/cluster/prod.foo.k8s.local" = "owned"
  }
}