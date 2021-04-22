#################
# Private subnet
#################
resource "aws_subnet" "private" {

  vpc_id                          = var.vpc_id
  cidr_block                      = var.private_subnets_cidr[count.index]
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  availability_zone_id            = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) == 0 ? element(var.azs, count.index) : null

  tags = merge(
  {
    "Name" = format(
    "%s-${var.private_subnet_suffix}-%s",
    var.name,
    element(var.azs, count.index),
    )
  },
  var.tags,
  var.private_subnets_tags,
  )
}
#################
# Private routes
# There are as many routing tables as the number of NAT gateways
#################
resource "aws_route_table" "private" {
  vpc_id = var.vpc_id
  tags = merge(
  {
    "Name" = var.single_nat_gateway ? "${var.name}-${var.private_subnet_suffix}" : format(
    "%s-${var.private_subnet_suffix}-%s",
    var.name,
    element(var.azs, count.index),
    )
  },
  var.tags,
  var.private_route_table_tags,
  )
}