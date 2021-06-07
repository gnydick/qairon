resource "aws_route_table" "public" {
  count = length(var.azs)
  vpc_id = var.vpc_id

  tags = {
    "Name" = format("%s-%s.rtbl", var.global_strings["regional_prefix"], element(var.azs, count.index))
    "Tier" = "public"
    "Az" = element(var.azs, count.index)
  }


  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_route_table" "private" {
  count = length(var.azs)
  tags = {
    "Name" = format("%s-%s.rtbl", var.global_strings["regional_prefix"], element(var.azs, count.index))
    "Tier" = "private"
    "Az" = element(var.azs, count.index)
  }
  vpc_id = var.vpc_id



  lifecycle {
    create_before_destroy = true
  }
}


module "private" {
  for_each = var.private_subnet_cidrs
  source = "./private_subnet"
  private_subnet_cidrs = each.value
  azs = var.azs
  vpc_id = var.vpc_id
  subnet_type = each.key
  route_table_ids = aws_route_table.private.*.id
  depends_on = [aws_route_table.private, aws_route_table.public]
}


module "public" {
  for_each = var.public_subnet_cidrs
  source = "./public_subnet"
  azs = var.azs
  vpc_id = var.vpc_id
  subnet_type = each.key
  public_subnet_cidrs = each.value
  route_table_ids = aws_route_table.public.*.id
  depends_on = [aws_route_table.private, aws_route_table.public]
}


#########################################
resource "aws_route" "private_def_nat_gw" {
  count = length(var.azs)
  route_table_id = element(aws_route_table.private.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id = element(aws_nat_gateway.inet_access.*.id, count.index)
  depends_on = [aws_nat_gateway.inet_access, module.public, module.private, aws_route_table.private, aws_route_table.public]

}


##################################################








resource "aws_network_acl" "allow_all" {

  vpc_id = var.vpc_id
  subnet_ids = flatten([ [for k, subnets in module.public : subnets
  .public_subnet_ids], [for k, subnets in module.private : subnets
  .private_subnet_ids]])
  depends_on = [module.public, module.private]


  lifecycle {
    ignore_changes = [tags]
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


resource "aws_route" "public_def_gw" {
  count = length(var.azs)
  route_table_id = element(aws_route_table.public.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = aws_internet_gateway.public.id
  depends_on = [module.public, module.private, aws_route_table.private, aws_route_table.public]

}

resource "aws_internet_gateway" "public" {
  vpc_id = var.vpc_id
  tags = {
    "Name" = format("%s.igw", var.global_strings.regional_prefix),
  }
  depends_on = [module.public, module.private, aws_route_table.public, aws_route_table.private]

}


resource "aws_nat_gateway" "inet_access" {
  count = length(var.azs)
  allocation_id = element(aws_eip.nat.*.id, count.index)
  subnet_id = element(module.public["nat_gw"].public_subnet_ids, count.index)
  depends_on = [module.public, module.private]

  lifecycle {
    create_before_destroy = false
    ignore_changes = [tags]
  }

}


resource "aws_eip" "nat" {
  count = length(var.azs)
  vpc = true
  depends_on = [module.public, module.private]

  lifecycle {
    create_before_destroy = true
    ignore_changes = [tags]
  }
}

output "private_subnet_ids" {
  value = tomap({
  for type, subnets in module.private : type => subnets.private_subnet_ids
  })
}

output "public_subnet_ids" {
  value = tomap({
    for k, subtype in module.public : k => subtype.public_subnet_ids
  })
//  value = module.public.public_subnet_ids
}


output "private_route_table_ids" {
  value = aws_route_table.private.*.id
}

output "public_route_table_ids" {
  value = aws_route_table.public.*.id
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
