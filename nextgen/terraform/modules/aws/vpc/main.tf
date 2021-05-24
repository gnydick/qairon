######
# VPC
######
resource "aws_vpc" "vpc" {
  cidr_block           = var.vpc_config.cidr
  enable_dns_hostnames = var.vpc_config.enable_dns_hostnames
  enable_dns_support   = var.vpc_config.enable_dns_support

  tags = {
    "Name" : format("%s-%s", var.global_strings.regional_prefix, var.vpc_config.name)
  }


}
