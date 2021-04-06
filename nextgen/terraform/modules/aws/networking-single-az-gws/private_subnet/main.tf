#--------------------------------------------------------------
# This module creates all resources necessary for a private
# subnet
#--------------------------------------------------------------

variable "config_name" {}

variable "vpc_id" {}


variable "azs" {
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

resource "aws_subnet" "private" {
  vpc_id            = "${var.vpc_id}"
  cidr_block        = "${element(var.private_subnet_cidrs, count.index)}"
  availability_zone = "${element(var.azs, count.index)}"
  count             = "${length(var.private_subnet_cidrs)}"


  tags =    "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${local.prefix}.${element(var.azs, count.index)}.${count.index}.private.subnet"),
                    map("Config","${var.config_name}"),
                    map("GeneratedBy", "terraform"),
                    map("AZ", "${element(var.azs, count.index)}"),
                    map("SubnetIndex", "${count.index}"),
                    map("Tier", "private"),
                    var.kube_extra_tags,
                    var.extra_tags)}"

  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = false

}

variable "environment" {}

variable "region" {}



variable "private_subnet_cidrs" {
  type = "list"
}


output "private_subnet_ids" {
  value = ["${aws_subnet.private.*.id}"]
}

