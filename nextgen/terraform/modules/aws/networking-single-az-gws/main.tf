locals {
  prefix = "${var.environment}.${var.region}.${var.vpc_id}"
}

module "public" {
  source      = "./public_subnet"
  region      = var.region
  config_name = var.config_name
  environment = var.environment
  azs = [
    var.azs,
  ]
  vpc_id = var.vpc_id
  public_subnet_cidrs = [
    var.public_subnet_cidrs,
  ]
  extra_tags      = var.extra_tags["public"]
  kube_extra_tags = var.kube_extra_tags["public"]
}

module "private" {
  source = "./private_subnet"
  private_subnet_cidrs = [
    var.private_subnet_cidrs,
  ]
  region      = var.region
  config_name = var.config_name
  environment = var.environment
  azs = [
    var.azs,
  ]
  vpc_id          = var.vpc_id
  extra_tags      = var.extra_tags["private"]
  kube_extra_tags = var.kube_extra_tags["private"]
}

resource "aws_network_acl" "allow_all" {
  vpc_id = var.vpc_id
  subnet_ids = [
    module.private.private_subnet_ids,
    module.public.public_subnet_ids,
  ]

  ingress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  egress {
    protocol   = "-1"
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }
  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.allow_all.network_acl"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "Tier" = "public"
    },
    var.extra_tags["public"],
  )
}

resource "aws_nat_gateway" "inet_access" {
  allocation_id = aws_eip.nat.id
  subnet_id     = element(module.public.public_subnet_ids, count.index)

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [tags]
  }

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.nat_gateway"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "SubnetIndex" = count.index
    },
    {
      "Tier" = "public"
    },
    var.extra_tags["public"],
  )
}

resource "aws_route" "private_def_nat_gw" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.inet_access.id
}

resource "aws_eip" "nat" {
  vpc = true
  lifecycle {
    create_before_destroy = true
    ignore_changes        = [tags]
  }

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.nat.eip"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "Tier" = "public"
    },
    var.extra_tags["public"],
  )
}

resource "aws_route" "public_def_gw" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.public.id
}

resource "aws_internet_gateway" "public" {
  vpc_id = var.vpc_id
  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.public.internet_gateway"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "Tier" = "public"
    },
    var.extra_tags["public"],
  )
}

resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = element(module.public.public_subnet_ids, count.index)
  route_table_id = aws_route_table.public.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route_table" "public" {
  vpc_id = var.vpc_id

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.public.route_table"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "Tier" = "public"
    },
    var.extra_tags["public"],
  )

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route_table" "private" {
  vpc_id = var.vpc_id
  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.private.route_table"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "Tier" = "private"
    },
    var.extra_tags["private"],
  )

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route_table_association" "private" {
  count          = length(var.private_subnet_cidrs)
  subnet_id      = element(module.private.private_subnet_ids, count.index)
  route_table_id = aws_route_table.private.id

  lifecycle {
    create_before_destroy = true
  }
}

output "private_subnet_ids" {
  value = [
    module.private.private_subnet_ids,
  ]
}

output "public_subnet_ids" {
  value = [
    module.public.public_subnet_ids,
  ]
}

output "private_route_table_id" {
  value = aws_route_table.private.id
}

output "public_route_table_id" {
  value = aws_route_table.public.id
}

//extra_tags = {
//  public = {
//    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
//    "kubernetes.io/role/elb" = ""
//  },
//  private = {
//    "kubernetes.io/cluster/${local.cluster_name}" = "shared"
//    "kubernetes.io/role/internal-elb" = ""
//  }
//}
