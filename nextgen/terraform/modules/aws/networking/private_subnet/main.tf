#################
# Private subnet
#################
resource "aws_subnet" "private" {

  count = length(var.private_subnets)

  vpc_id                          = var.vpc_id
  cidr_block                      = var.private_subnets[count.index]
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  availability_zone_id            = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) == 0 ? element(var.azs, count.index) : null

  tags = merge(
  {
    "Name" = format(
    "%s-${var.private_subnet_suffix}-%s",
    var.environment,
    element(var.azs, count.index),
    )
  },
  var.tags,
  var.private_subnet_tags,
  )
}