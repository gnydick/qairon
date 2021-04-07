#--------------------------------------------------------------
# This module creates all resources necessary for a subnet
# subnet
#--------------------------------------------------------------

locals {
  prefix = "${var.environment}.${var.region}.${var.vpc_id}"
}

resource "aws_subnet" "subnet" {
  count             = length(var.subnet_cidrs)
  vpc_id            = var.vpc_id
  cidr_block        = element(var.subnet_cidrs, count.index)
  availability_zone = element(var.azs, count.index)

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.${element(var.azs, count.index)}.${count.index}.addon.subnet"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "AZ" = element(var.azs, count.index)
    },
    {
      "SubnetIndex" = count.index
    },
    {
      "Tier" = var.tier
    },
    var.kube_extra_tags,
    var.extra_tags,
  )

  lifecycle {
    create_before_destroy = true
  }

  map_public_ip_on_launch = false
}

resource "aws_route_table_association" "subnet" {
  count          = length(var.subnet_cidrs)
  subnet_id      = element(aws_subnet.subnet.*.id, count.index)
  route_table_id = element(var.route_table_ids, count.index)

  lifecycle {
    create_before_destroy = true
  }
}

output "subnet_ids" {
  value = [
    aws_subnet.subnet.*.id,
  ]
}

