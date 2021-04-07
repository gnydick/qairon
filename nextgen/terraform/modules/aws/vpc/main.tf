#--------------------------------------------------------------
# This module creates all resources necessary for a VPC
#--------------------------------------------------------------

resource "aws_vpc" "vpc" {
  cidr_block           = var.cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${var.environment}.${var.region}.${var.vpc_number}.vpc"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    var.extra_tags,
  )

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [tags]
  }
}

output "vpc_id" {
  value = aws_vpc.vpc.id
}

output "vpc_cidr" {
  value = aws_vpc.vpc.cidr_block
}

