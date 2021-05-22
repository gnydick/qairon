module "private" {
  for_each = var.private_subnet_cidrs
  source = "./private_subnet"
  private_subnet_cidrs = each.value
  azs = var.azs
  vpc_id = var.vpc_id
  subnet_type = each.key
}


output "private_subnet_ids" {
  value = tomap({
  for k, ids in module.private : k => ids
  })
}


module "public" {
  source = "./public_subnet"
  azs = var.azs
  vpc_id = var.vpc_id
  public_subnet_cidrs = var.public_subnet_cidrs
}



resource "aws_network_acl" "allow_all" {
  depends_on = [module.private]

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
  depends_on = [module.public, module.private]

  count = length(var.azs)
  allocation_id = element(aws_eip.nat.*.id, count.index)
  subnet_id = element(module.public.public_subnet_ids, count.index)

  lifecycle {
    create_before_destroy = true

    ignore_changes = ["tags"]

  }

}

resource "aws_route" "private_def_nat_gw" {
  depends_on = [module.public, module.private, aws_eip.nat]

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
  count = length(aws_route_table.public)
  route_table_id = element(aws_route_table.public.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  gateway_id = element(aws_internet_gateway.public.*.id, count.index)
}

resource "aws_internet_gateway" "public" {
  count = length(var.azs)
  vpc_id = var.vpc_id
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



  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_route_table" "private" {
  count = length(var.azs)
  vpc_id = var.vpc_id


  lifecycle {
    create_before_destroy = true
  }
}
resource "aws_route_table_association" "private" {
  count = length(var.private_subnet_cidrs)
//  depends_on = [module.private]
  subnet_id = element(module.private.private_subnet_ids, count.index)
  route_table_id = element(aws_route_table.private.*.id, count.index)

  lifecycle {
    create_before_destroy = true
  }
}


// duplicate
//resource "aws_route_table_association" "priv_to_nat" {
//  count = "${length(var.private_subnet_cidrs)}"
//  subnet_id = "${element(module.private.private_subnet_ids, count.index)}"
//  route_table_id = "${element(aws_route_table.private.*.id, count.index)}"
//}


//output "private_subnet_ids" {
//  value = [
//    module.private.private_subnet_ids]
//}

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
