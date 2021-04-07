resource "aws_vpc_peering_connection_accepter" "accepter" {
  count                     = var.status == "pending-acceptance" ? 1 : 0
  auto_accept               = true
  vpc_peering_connection_id = data.aws_vpc_peering_connection.requester-vpc.id

  tags = {
    Side        = "Accepter"
    Source      = var.initiating-vpc-id
    Destination = var.requested-vpc-id
  }
}

//resource "aws_route" "pub_subnets_to_initiator" {
//  count = "${length(data.aws_route_tables.requsted-public-routing-tables.ids)}"
//  route_table_id = "${element(data.aws_route_tables.requsted-public-routing-tables.ids, count.index )}"
//  vpc_peering_connection_id = "${data.aws_vpc_peering_connection.requested-vpc.id}"
//  destination_cidr_block = "${var.initiating-cidr}"
//}

resource "aws_route" "priv_subnets_to_initiator" {
  count = var.status == "active" ? length(data.aws_route_tables.requsted-private-routing-tables.ids) : 0
  route_table_id = element(
    tolist(data.aws_route_tables.requsted-private-routing-tables.ids),
    count.index,
  )
  vpc_peering_connection_id = data.aws_vpc_peering_connection.requester-vpc.id
  destination_cidr_block    = var.initiating-cidr
}

