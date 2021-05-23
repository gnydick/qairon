#--------------------------------------------------------------
# This module creates all resources necessary for a private
# subnet
#--------------------------------------------------------------

variable "route_table_ids" {
  type = list(string)
}

variable "private_subnet_cidrs" {
  type = list(string)
}


variable "vpc_id" {}


variable "azs" {
  type = list(string)
}

variable "subnet_type" {
  type = string
}



resource "aws_route_table_association" "private" {
  count          = length(var.private_subnet_cidrs)
  subnet_id      = element(aws_subnet.private.*.id, count.index)
  route_table_id = element(var.route_table_ids, count.index)

  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = var.vpc_id
  cidr_block        = element(var.private_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)

  tags = {
    "Tier" : "private"
    "Use" : var.subnet_type
    "Name": format("%s%s", var.subnet_type, count.index)
  }

  lifecycle {
    create_before_destroy = true
  }
  map_public_ip_on_launch = false
}




output "private_subnet_ids" {
  value = aws_subnet.private.*.id
}
