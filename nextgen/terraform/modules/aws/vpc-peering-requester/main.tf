

resource "aws_vpc_peering_connection" "requester_to_accepter" {
  vpc_id = "${var.requester_vpc_id}"
  peer_vpc_id = "${var.accepter_vpc_id}"
  peer_owner_id = "${var.accepter_account}"




  tags {
    Name = "${var.requester_vpc_id}_${var.accepter_vpc_id}"
    Side = "Requester"
    Source = "${var.requester_vpc_id}"
    Destination = "${var.accepter_vpc_id}"
  }
}


resource "aws_route" "subnets_to_accepter" {
  count = "${length(var.requester_private_route_table_ids)}"
  route_table_id = "${element(var.requester_private_route_table_ids, count.index )}"
  vpc_peering_connection_id = "${aws_vpc_peering_connection.requester_to_accepter.id}"
  destination_cidr_block = "${var.accepter_cidr}"

}