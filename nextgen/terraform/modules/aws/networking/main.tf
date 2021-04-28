module "public" {
  source      = "./public_subnet"
  environment = var.environment
  azs = var.azs
  vpc_id = var.vpc_id
  public_subnets = var.public_subnets
  public_subnet_tags = var.public_subnet_tags
}

module "private" {
  source = "./private_subnet"
  environment = var.environment
  azs = var.azs
  vpc_id = var.vpc_id
  private_subnets = var.private_subnets
  private_subnet_tags = var.private_subnet_tags
}

###################
# Internet Gateway
###################
resource "aws_internet_gateway" "igw" {
  vpc_id = var.vpc_id
  tags = merge(
  {
    "Name" = format("%s", var.environment)
  },
  var.tags,
  )
}

################
# Public routes
################
resource "aws_route_table" "public_rt" {
  vpc_id = var.vpc_id
  tags = merge(
  {
    "Name" = format("%s-${var.public_subnet_suffix}", var.environment)
  },
  var.tags,
  )
}

resource "aws_route" "public_internet_gateway" {
  route_table_id         = aws_route_table.public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
  timeouts {
    create = "5m"
  }
}

resource "aws_route_table_association" "public" {
  count = length(var.public_subnets) > 0 ? length(var.public_subnets) : 0
  subnet_id      = module.public.public_subnets_ids
  route_table_id = aws_route_table.public_rt.id
}

###########################################
## NAT Gateways
###########################################
#
#resource "aws_eip" "nat" {
#  count = var.enable_nat_gateway && false == var.reuse_nat_ips ? local.nat_gateway_count : 0
#
#  vpc = true
#
#  tags = merge(
#  {
#    "Name" = format(
#    "%s-%s",
#    var.name,
#    element(var.azs, var.single_nat_gateway ? 0 : count.index),
#    )
#  },
#  var.tags,
#  var.nat_eip_tags,
#  )
#}
#
#resource "aws_nat_gateway" "nat_gtw" {
#  count = length(var.public_subnets)
#
#  allocation_id = element(local.nat_gateway_ips)
#  subnet_id = element(module.public.public_subnets_ids)
#  tags = merge(
#  {
#    "Name" = format(
#    "%s-%s",
#    var.name,
#    element(var.azs, count.index),
#    )
#  },
#  var.tags,
#  var.nat_gateway_tags,
#  )
#
#  depends_on = [aws_internet_gateway.igw]
#}
#
#resource "aws_route" "private_nat_gateway" {
#  count = element(module.public.public_subnets_ids) >= 0
#
#  route_table_id         = element(aws_route_table.private.*.id, count.index)
#  destination_cidr_block = "0.0.0.0/0"
#  nat_gateway_id         = element(aws_nat_gateway.nat_gtw.*.id, count.index)
#
#  timeouts {
#    create = "5m"
#  }
#}
