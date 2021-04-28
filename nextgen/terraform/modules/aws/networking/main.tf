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
  subnet_id      = element(module.public.public_subnets_ids, count.index)
  route_table_id = aws_route_table.public_rt.id
}

##########################################
# NAT Gateways
##########################################

resource "aws_eip" "nat" {
  count = length(var.azs) > 0 ? length(var.azs) : 0

  vpc = true

  tags = merge(
  {
    "Name" = format(
    "%s-%s",
    var.environment,
    element(var.azs ? 0 : count.index),
    )
  },
  var.tags,
  )
}

resource "aws_nat_gateway" "nat_gtw" {
  count = length(var.azs) > 0 ? length(var.azs) : 0

  allocation_id = element(local.nat_gateway_ips)
  subnet_id = element(module.public.public_subnets_ids)
  tags = merge(
  {
    "Name" = format(
    "%s-%s",
    var.environment,
    element(var.azs, count.index),
    )
  },
  var.tags,
  var.nat_gateway_tags,
  )

  depends_on = [aws_internet_gateway.igw]
}

################
# Private routes
################

resource "aws_route_table" "private_rt" {
  count = length(var.private_subnets) > 0 ? length(var.private_subnets) : 0

  vpc_id = var.vpc_id

  tags = merge(
  {
    "Name" = format(
    "%s-${var.private_subnet_suffix}-%s",
    var.environment,
    element(var.azs, count.index),
    )
  },
  var.tags,
  var.private_route_table_tags,
  )
}

resource "aws_route" "private_nat_gateway" {
  count = length(var.private_subnets) > 0 ? length(var.private_subnets) : 0

  route_table_id         = element(aws_route_table.private_rt.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = element(aws_nat_gateway.nat_gtw.*.id, count.index)

  timeouts {
    create = "5m"
  }
}

resource "aws_route_table_association" "private" {
  count = length(var.private_subnets) > 0 ? length(var.private_subnets) : 0

  subnet_id = element(module.private.private_subnets_ids, count.index)
  route_table_id = element(
  aws_route_table.private_rt.*.id,
  count.index,
  )
}
