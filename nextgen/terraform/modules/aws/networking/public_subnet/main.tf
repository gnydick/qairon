#################
# Private subnet
#################
resource "aws_subnet" "public" {
  vpc_id                          = var.vpc_id
  cidr_block                      = element(concat(var.public_subnets, [""]), count.index)
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  availability_zone_id            = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) == 0 ? element(var.azs, count.index) : null
  map_public_ip_on_launch         = var.map_public_ip_on_launch

  tags = merge(
  {
    "Name" = format(
    "%s-${var.public_subnet_suffix}-%s",
    var.name,
    element(var.azs, count.index),
    )
  },
  var.tags,
  var.public_subnet_tags,
  )
}

###################
# Internet Gateway
###################
resource "aws_internet_gateway" "this" {
  vpc_id = var.vpc_id
  tags = merge(
  {
    "Name" = format("%s", var.name)
  },
  var.tags,
  var.igw_tags,
  )
}

################
# Public routes
################
resource "aws_route_table" "public" {
  vpc_id = var.vpc_id
  tags = merge(
  {
    "Name" = format("%s-${var.public_subnet_suffix}", var.name)
  },
  var.tags,
  var.public_route_table_tags,
  )
}

resource "aws_route" "public_internet_gateway" {
  route_table_id         = aws_route_table.public[0].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this[0].id
  timeouts {
    create = "5m"
  }
}