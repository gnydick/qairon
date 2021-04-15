data "aws_route53_zone" "infra" {
  name = "infra.foo.net"
}

data "aws_subnet_ids" "private_nets" {
  vpc_id = "${var.vpc_id}"

  tags {

    Tier = "private"
  }
}

data "aws_elb" "elb" {

  tags = "${map("kubernetes.io/service-name","infra/openvpn-infra")}"
  name = "a555b9047a81811e9995a0a27fb28875"
}
