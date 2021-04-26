module "public" {
  source      = "./public_subnet"
  environment = var.environment
  azs = var.azs
  vpc_id = var.vpc_id
  public_subnet_cidr = var.public_subnet_cidr
  public_subnet_tags = var.public_subnet_tags
}

module "private" {
  source = "./private_subnet"
  environment = var.environment
  azs = var.azs
  vpc_id = var.vpc_id
  private_subnet_cidr = var.private_subnet_cidr
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

##########################################
# NAT Gateways (Work in Progress)
##########################################

resource "aws_nat_gateway" "nat_gtw" {
  count = length(var.public_subnet_cidr)

  allocation_id = element(
  local.nat_gateway_ips,
  var.single_nat_gateway ? 0 : count.index,
  )
  subnet_id = element(
  aws_subnet.public.*.id,
  var.single_nat_gateway ? 0 : count.index,
  )

  tags = merge(
  {
    "Name" = format(
    "%s-%s",
    var.name,
    element(var.azs, var.single_nat_gateway ? 0 : count.index),
    )
  },
  var.tags,
  var.nat_gateway_tags,
  )

  depends_on = [aws_internet_gateway.igw]
}

resource "aws_route" "private_nat_gateway" {
  count = var.create_vpc && var.enable_nat_gateway ? local.nat_gateway_count : 0

  route_table_id         = element(aws_route_table.private.*.id, count.index)
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = element(aws_nat_gateway.this.*.id, count.index)

  timeouts {
    create = "5m"
  }
}
