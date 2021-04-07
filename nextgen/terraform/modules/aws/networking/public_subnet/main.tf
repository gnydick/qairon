#--------------------------------------------------------------
# This module creates all resources necessary for a public
# subnet
#--------------------------------------------------------------
variable "config_name" {
}

variable "vpc_id" {
}

variable "azs" {
  type = list(string)
}

variable "public_subnet_cidrs" {
  type = list(string)
}

locals {
  prefix = "${var.environment}.${var.region}.${var.vpc_id}"
}

variable "extra_tags" {
  type = map(string)
}

variable "kube_extra_tags" {
  type = map(string)
}

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

variable "environment" {
}

variable "region" {
}

output "public_subnet_ids" {
  value = [aws_subnet.public.*.id]
}

