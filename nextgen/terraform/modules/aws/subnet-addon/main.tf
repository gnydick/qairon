
#--------------------------------------------------------------
# This module creates all resources necessary for a subnet
# subnet
#--------------------------------------------------------------


locals {
  prefix = "${var.environment}.${var.region}.${var.vpc_id}"
}

resource "aws_subnet" "subnet" {
  count = "${length(var.subnet_cidrs)}"
  vpc_id = "${var.vpc_id}"
  cidr_block = "${element(var.subnet_cidrs, count.index)}"
  availability_zone = "${element(var.azs, count.index)}"

  tags = "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${local.prefix}.${element(var.azs, count.index)}.${count.index}.addon.subnet"),
                    map("Config","${var.config_name}"),
                    map("GeneratedBy", "terraform"),
                    map("AZ", "${element(var.azs, count.index)}"),
                    map("SubnetIndex", "${count.index}"),
                    map("Tier", "${var.tier}"),
                    var.kube_extra_tags,
                    var.extra_tags)}"

  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = false

}


resource "aws_route_table_association" "subnet" {
  count = "${length(var.subnet_cidrs)}"
  subnet_id = "${element(aws_subnet.subnet.*.id, count.index)}"
  route_table_id = "${element(var.route_table_ids, count.index)}"

  lifecycle {
    create_before_destroy = true
  }
}


output "subnet_ids" {
  value = [
    "${aws_subnet.subnet.*.id}"]
}

