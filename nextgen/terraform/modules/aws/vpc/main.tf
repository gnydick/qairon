######
# VPC
######
locals {
  name = "${var.name_prefix}-${var.number}-vpc"
}

resource "aws_vpc" "vpc" {

  cidr_block                       = var.cidr
  enable_dns_hostnames             = var.enable_dns_hostnames
  enable_dns_support               = var.enable_dns_support

  tags = merge(
    {
      "Name" = local.name
    },
    var.tags,
    var.vpc_tags,
  )

}
