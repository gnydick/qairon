module "accepter" {
  source = "../../../../../modules/aws/vpc-peering-accepter"

  initiating-cidr = "${var.requesting-cidr}"
  initiating-vpc-id = "${var.requesting-vpc_id}"
  requested-vpc-id = "${var.accepter-vpc_id}"
  status = "${var.status}"

  allow_dns_in = "${var.status=="active"?var.allow_dns_in:false}"
}


data "aws_vpc_peering_connection" "accepter" {
  cidr_block = "${var.requesting-cidr}"
  status = "${var.status}"
}

resource "aws_vpc_peering_connection_options" "accepter_options"{
  count="${var.status=="active"?1:0}"
  vpc_peering_connection_id = "${data.aws_vpc_peering_connection.accepter.id}"
  accepter {
    allow_remote_vpc_dns_resolution = "${var.allow_dns_in}"
  }
}