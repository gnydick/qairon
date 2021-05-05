module "vpc" {
  source = "../../../../../../../../modules/aws/vpc"
  cidr = var.vpc_cidr
  name = "${var.region}-${var.environment}"
  tags = {
    "Region" = var.region
    "Environment" = var.environment
    "GeneratedBy" = "terraform"
  }
}

# resource "aws_vpc_ipv4_cidr_block_association" "additional_cidrs" {
#   count="${length(var.vpc_add_cidrs)}"
#   cidr_block = "${element(values(var.vpc_add_cidrs),count.index)}"
#   vpc_id = "${module.vpc.vpc_id}"
# }
