#################
# Public subnet
#################
resource "aws_subnet" "public" {

  count = length(var.public_subnet_cidr)

  vpc_id                          = var.vpc_id
  cidr_block                      = var.public_subnet_cidr[count.index]
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  availability_zone_id            = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) == 0 ? element(var.azs, count.index) : null
  map_public_ip_on_launch         = var.map_public_ip_on_launch

  tags = merge(
  {
    "Name" = format(
    "%s-${var.public_subnet_suffix}-%s",
    var.environment,
    element(var.azs, count.index),
    )
  },
  var.tags,
  var.public_subnet_tags,
  )
}
