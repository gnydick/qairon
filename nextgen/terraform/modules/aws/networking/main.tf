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
