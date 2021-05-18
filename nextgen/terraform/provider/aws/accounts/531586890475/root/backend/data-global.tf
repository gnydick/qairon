data "aws_caller_identity" "core-lib" {
}

data "aws_availability_zones" "available" {
  state = "available"
}

variable "org" {}
variable "dept" {}
variable "environment" {}
variable "role" {}
variable "config" {}
variable "region" {}
variable "provider_region" {}


locals {
  global_prefix = "${var.org}-${var.dept}-${var.environment}-${var.role}-${var.config}"
  regional_prefix = "${var.org}-${var.dept}-${var.environment}-${var.region}-${var.role}-${var.config}"
  global_tags = {
    Org = var.org,
    Dept = var.dept,
    Environment = var.environment,
    Role = var.role,
    Config = var.config,
    GeneratedBy = "terraform"
  }
  regional_tags = merge(
  local.global_tags,
  {
    "Region" = var.region
  }
  )
  global_strings = {
    global_prefix = local.global_prefix,
    regional_prefix = local.regional_prefix
  }
  global_maps = {
    global_tags = local.global_tags,
    regional_tags = local.regional_tags
  }
}

output "account_id" {
  value = data.aws_caller_identity.core-lib.account_id
}

output "global_prefix" {
  value = local.global_prefix
}

output "regional_prefix" {
  value = local.regional_prefix
}

output "global_tags" {
  value = local.global_tags
}

output "regional_tags" {
  value = local.regional_tags
}

output "global_strings" {
  value = local.global_strings
}

output "global_maps" {
  value = local.global_maps
}