data "aws_route_tables" "requsted-private-routing-tables" {
  vpc_id = "${var.requested-vpc-id}"
  tags {
    Tier = "private"
  }
}

data "aws_vpc_peering_connection" "requester-vpc" {
  vpc_id = "${var.initiating-vpc-id}"
  peer_vpc_id = "${var.requested-vpc-id}"
  status = "${var.status}"

}


//data "aws_route_tables" "requsted-public-routing-tables" {
//  vpc_id = "${var.requested-vpc-id}"
//  tags {
//    Tier = "public"
//
//  }
//}