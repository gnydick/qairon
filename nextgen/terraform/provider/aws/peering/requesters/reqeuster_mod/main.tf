data "aws_vpc" "requester_vpc" {
  tags = {
    Name = var.requester_vpc
  }
}

data "aws_route_tables" "requester-private-routing-tables" {
  vpc_id = var.requester_vpc_id
  tags = {
    NgDev1Peer = "true"
  }
}

module "requester" {
  source                            = "../../../../../modules/aws/vpc-peering-requester"
  accepter_account                  = var.accepter-account
  accepter_cidr                     = var.accepter-cidr
  accepter_vpc_id                   = var.accepter-vpc_id
  region                            = var.region
  requester_cidr                    = var.requester_cidr
  requester_private_route_table_ids = data.aws_route_tables.requester-private-routing-tables.ids
  requester_vpc                     = var.requester_vpc
  requester_vpc_id                  = var.requester_vpc_id
  allow_dns_out                     = var.allow_dns_out
}

resource "aws_vpc_peering_connection_options" "requester_options" {
  count                     = var.status == "active" ? 1 : 0
  vpc_peering_connection_id = module.requester.requester_id
  requester {
    allow_remote_vpc_dns_resolution = var.allow_dns_out
  }
}

