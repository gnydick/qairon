#--------------------------------------------------------------
# This module creates all resources necessary for a private
# subnet
#--------------------------------------------------------------

variable "vpc_id" {}


variable "azs" {
  type = list(string)
}

variable "subnet_type" {
  type = string
}

resource "aws_subnet" "private" {
  vpc_id            = var.vpc_id
  cidr_block        = element(var.private_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)
  count             = length(var.private_subnet_cidrs)

  tags = {
    "Tier": "private"
  }


  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = false

}



variable "private_subnet_cidrs" {
  type = list(string)
}


output "private_subnet_ids" {
  value = aws_subnet.private.*.id
}
