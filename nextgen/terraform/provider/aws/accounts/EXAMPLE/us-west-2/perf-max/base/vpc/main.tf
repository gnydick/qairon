module "vpc" {
  source = "../../../../../../../../modules/aws/vpc"
  config_name = "${var.config_name}"
  cidr = "${var.vpc_cidr}"
  region = "${var.region}"
  environment = "${var.environment}"
  extra_tags = "${var.extra_tags}"
  vpc_number = "${var.vpc_number}"
}

resource "aws_vpc_ipv4_cidr_block_association" "additional_cidrs" {
  count="${length(var.vpc_add_cidrs)}"
  cidr_block = "${element(values(var.vpc_add_cidrs),count.index)}"
  vpc_id = "${module.vpc.vpc_id}"
}
