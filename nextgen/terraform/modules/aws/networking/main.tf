#################
# Public subnet
#################
resource "aws_subnet" "public" {

  count = length(var.public_subnets)

  vpc_id                  = var.vpc_id
  cidr_block              = var.public_subnets[count.index]
  availability_zone       = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  availability_zone_id    = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) == 0 ? element(var.azs, count.index) : null
  map_public_ip_on_launch = var.map_public_ip_on_launch

  tags = {
    "Name" = format("%s-%s", var.global_strings.regional_prefix, var.azs[count.index]),
    "Az"   = var.azs[count.index]
    "Tier" = "public"
  }


}

#################
# Private subnet
#################
resource "aws_subnet" "private" {

  count = length(var.private_subnets)

  vpc_id               = var.vpc_id
  cidr_block           = var.private_subnets[count.index]
  availability_zone    = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  availability_zone_id = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) == 0 ? element(var.azs, count.index) : null

  tags = {
    "Name" = format("%s-%s", var.global_strings.regional_prefix, var.azs[count.index]),
    "Az"   = var.azs[count.index]
    "Tier" = "private"
  }
}

###################
# Internet Gateway
###################
resource "aws_internet_gateway" "igw" {
  count  = length(var.public_subnets) > 0 ? 1 : 0
  vpc_id = var.vpc_id
  tags = {
    "Name" = format("%s-%s", var.global_strings.regional_prefix, var.azs[count.index]),
    "Az"   = var.azs[count.index]
  }
}

################
# Public routes
################
resource "aws_route_table" "public_rt" {
  count  = length(var.public_subnets) > 0 ? 1 : 0
  vpc_id = var.vpc_id
  tags = {
    "Name" = format("%s-%s", var.global_strings.regional_prefix, var.azs[count.index]),
    "Az"   = var.azs[count.index]
  }
}

resource "aws_route" "public_internet_gateway" {
  count                  = length(var.public_subnets) > 0 ? 1 : 0
  route_table_id         = aws_route_table.public_rt[0].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw[0].id
  timeouts {
    create = "5m"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(var.public_subnets) > 0 ? length(var.public_subnets) : 0
  subnet_id      = element(aws_subnet.public.*.id, count.index)
  route_table_id = element(aws_route_table.public_rt.*.id, count.index)
}

##########################################
# NAT Gateways
##########################################

resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? local.nat_gateway_count : 0

  vpc = true
  tags = {
    "Name" = format("%s-%s", var.global_strings.regional_prefix, var.azs[count.index]),
    "Az"   = var.azs[count.index]
  }
}

resource "aws_nat_gateway" "nat_gtw" {
  count = var.enable_nat_gateway ? local.nat_gateway_count : 0

  allocation_id = element(local.nat_gateway_ips, count.index)
  subnet_id     = element(aws_subnet.public.*.id, count.index)
  tags = {
    "Name" = format("%s-%s", var.global_strings.regional_prefix, var.azs[count.index]),
    "Az"   = var.azs[count.index]
  }

  depends_on = [aws_internet_gateway.igw]
}

################
# Private routes
################

resource "aws_route_table" "private_rt" {
  count = local.max_subnet_length > 0 ? local.nat_gateway_count : 0

  vpc_id = var.vpc_id
  tags = {
    "Name" = format("%s-%s", var.global_strings.regional_prefix, var.azs[count.index]),
    "Az"   = var.azs[count.index]
  }
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

  subnet_id = element(aws_subnet.private.*.id, count.index)
  route_table_id = element(
    aws_route_table.private_rt.*.id,
    count.index,
  )
}
