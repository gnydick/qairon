#--------------------------------------------------------------
# This module creates all resources necessary for a public
# subnet
#--------------------------------------------------------------
resource "aws_subnet" "public" {
  vpc_id                  = var.vpc_id
  cidr_block              = element(var.public_subnet_cidrs, count.index)
  availability_zone       = element(var.azs, count.index)
  count                   = length(var.public_subnet_cidrs)
  map_public_ip_on_launch = true

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.${element(var.azs, count.index)}.${count.index}.public.subnet"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "AZ" = element(var.azs, count.index)
    },
    {
      "SubnetIndex" = count.index
    },
    {
      "Tier" = "public"
    },
    {
      "kubernetes.io/role/elb" = ""
    },
    var.kube_extra_tags,
    var.extra_tags,
  )

  lifecycle {
    create_before_destroy = true
  }
}
