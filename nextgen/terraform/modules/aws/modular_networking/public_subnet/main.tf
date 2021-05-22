#--------------------------------------------------------------
# This module creates all resources necessary for a public
# subnet
#--------------------------------------------------------------

variable "vpc_id" {}


variable "azs" {
  type = list
}



resource "aws_subnet" "public" {
  vpc_id            = var.vpc_id
  cidr_block        = element(var.public_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)
  count             = length(var.public_subnet_cidrs)

  tags = {
    "Tier": "public"
  }


  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = false

}



variable "public_subnet_cidrs" {
  type = list(string)
}


output "public_subnet_ids" {
  value = aws_subnet.public.*.id
}

