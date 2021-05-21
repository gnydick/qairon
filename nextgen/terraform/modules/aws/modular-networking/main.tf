locals {
  prefix = "${var.environment}.${var.region}.${var.vpc_id}"
}


module "public" {
  source = "public_subnet"
  region = var.region
  config_name = var.config_name
  environment = var.environment
  azs = [
    var.azs]
  vpc_id = var.vpc_id
  public_subnet_cidrs = [
    var.public_subnet_cidrs]
  extra_tags = var.extra_tags["public"]
  kube_extra_tags = var.kube_extra_tags["public"]
}

module "private" {
  source = "private_subnet"
  private_subnet_cidrs = [
    var.private_subnet_cidrs]
  region = var.region
  config_name = var.config_name
  environment = var.environment
  azs = [
    var.azs]
  vpc_id = var.vpc_id
  extra_tags = var.extra_tags["private"]
  kube_extra_tags = var.kube_extra_tags["private"]
  global_maps = var.global_maps
  global_strings = var.global_strings
}


resource "aws_network_acl" "allow_all" {
  vpc_id = var.vpc_id
  subnet_ids = [
    module.private.private_subnet_ids,
    module.public.public_subnet_ids
  ]

  lifecycle {
    ignore_changes = ["tags"]
  }

  ingress {
    protocol = "-1"
    rule_no = 100
    action = "allow"
    cidr_block = "0.0.0.0/0"
    from_port = 0
    to_port = 0
  }

  egress {
    protocol = "-1"
    rule_no = 100
    action = "allow"
    cidr_block = "0.0.0.0/0"
    from_port = 0
    to_port = 0
  }
}


resource "aws_nat_gateway" "inet_access" {
  count = length(var.azs)
  allocation_id = element(aws_eip.nat.*.id, count.index)
  subnet_id = element(module.public.public_subnet_ids, count.index)

  lifecycle {
    create_before_destroy = true

    ignore_changes = ["tags"]

  }

  tags = {
    "Tier" = "public"
  }

}

resource "aws_route" "private_def_nat_gw" {
  count = length(var.private_subnet_cidrs)
  route_table_id = element(aws_route_table.private.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = element(aws_nat_gateway.inet_access.*.id, count.index)
}


resource "aws_eip" "nat" {
  count = length(var.azs)
  vpc = true
  lifecycle {
    create_before_destroy = true
    ignore_changes = ["tags"]

  }


}


resource "aws_route" "public_def_gw" {
  count = aws_route_table.public.count
  route_table_id = element(aws_route_table.public.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = element(aws_internet_gateway.public.*.id, count.index)
}

resource "aws_internet_gateway" "public" {
  count = length(var.azs)
  vpc_id = var.vpc_id
  tags = {
    "Tier" = "public"
  }
}

resource "aws_route_table_association" "public" {
  count = length(var.public_subnet_cidrs)
  subnet_id = element(module.public.public_subnet_ids, count.index)
  route_table_id = element(aws_route_table.public.*.id, count.index)

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_route_table" "public" {
  count = length(var.azs)
  vpc_id = var.vpc_id


  tags = {
    "Tier" = "public"
  }

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_route_table" "private" {
  count = length(var.azs)
  vpc_id = var.vpc_id

  tags = {
    "Tier" = "private"
  }


  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)
  subnet_id = element(module.private.private_subnet_ids, count.index)
  route_table_id = element(aws_route_table.private.*.id, count.index)

  lifecycle {
    create_before_destroy = true
  }
}


output "private_subnet_ids" {
  value = [
    module.private.private_subnet_ids]
}

output "public_subnet_ids" {
  value = [
    module.public.public_subnet_ids]
}


output "private_route_table_ids" {
  value = aws_route_table.private.*.id
}

output "public_route_table_ids" {
  value = aws_route_table.public.*.id
}
