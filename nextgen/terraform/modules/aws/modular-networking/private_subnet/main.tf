#--------------------------------------------------------------
# This module creates all resources necessary for a private
# subnet
#--------------------------------------------------------------


variable "private_subnet_cidrs" {
  type = list(string)
}


variable "global_maps" {
  type = map(map(string))
}
variable "global_strings" {}


variable "vpc_id" {}

variable "azs" {
  type = list(string)
}


resource "aws_subnet" "private" {
  count = length(var.private_subnet_cidrs)
  vpc_id            = var.vpc_id
  cidr_block        = element(var.private_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)


  tags = {
    "Tier" = "private"
  }

  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = false

}

output "private_subnet_ids" {
  value = [aws_subnet.private.*.id]
}

resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)
  subnet_id = aws_subnet.private.id
  route_table_id = element(aws_route_table.private.*.id, count.index)

  lifecycle {
    create_before_destroy = true
  }
}
