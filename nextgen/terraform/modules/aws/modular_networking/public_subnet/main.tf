#--------------------------------------------------------------
# This module creates all resources necessary for a public
# subnet
#--------------------------------------------------------------

variable "subnet_type" {}

variable "vpc_id" {}


variable "azs" {
  type = list(any)
}

variable "route_table_ids" {
  type = list(string)
}


resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = var.vpc_id
  cidr_block        = element(var.public_subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)

  tags = {
    "Tier" : "public"
  }


  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = false

}

resource "aws_route_table_association" "public" {
  count = length(var.public_subnet_cidrs)
  subnet_id = element(aws_subnet.public.*.id, count.index)
  route_table_id = element(var.route_table_ids, count.index)

  lifecycle {
    create_before_destroy = true
  }
}

variable "public_subnet_cidrs" {
  type = list(string)
}


output "public_subnet_ids" {
  value = aws_subnet.public.*.id
}

