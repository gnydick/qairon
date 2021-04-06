#--------------------------------------------------------------
# This module creates all resources necessary for a public
# subnet
#--------------------------------------------------------------
variable "config_name" {}

variable "vpc_id" {}


variable "azs" {
  type = "list"
}

variable "public_subnet_cidrs" {
  type = "list"
}



locals {
  prefix = "${var.environment}.${var.region}.${var.vpc_id}"
}


variable "extra_tags" {
  type = "map"
}

variable "kube_extra_tags" {
  type = "map"
}

resource "aws_subnet" "public" {
  vpc_id = "${var.vpc_id}"
  cidr_block = "${element(var.public_subnet_cidrs, count.index)}"
  availability_zone = "${element(var.azs, count.index)}"
  count = "${length(var.public_subnet_cidrs)}"


  tags =    "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${local.prefix}.${element(var.azs, count.index)}.${count.index}.public.subnet"),
                    map("Config","${var.config_name}"),
                    map("GeneratedBy", "terraform"),
                    map("AZ", "${element(var.azs, count.index)}"),
                    map("SubnetIndex", "${count.index}"),
                    map("Tier", "public"),
                    map("kubernetes.io/role/elb",""),
                    var.kube_extra_tags,
                    var.extra_tags)}"


  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = true
}

variable "environment" {}

variable "region" {}




output "public_subnet_ids" {
  value = ["${aws_subnet.public.*.id}"]
}
