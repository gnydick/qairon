data "aws_caller_identity" "core-lib" {
}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  global_prefix = "${var.org}.${var.dept}.${var.environment}.${var.role}.${var.config}"
  regional_prefix = "${var.org}.${var.dept}.${var.environment}.${var.region}.${var.role}.${var.config}"
  global_tags = {
    Org = var.org
    Dept = var.dept
    Environment = var.environment
    Role = var.role
    Config = var.config
    GeneratedBy = "terraform"
  }

  regional_tags = merge(
  local.global_tags,
  {
    "Region" = var.region
  }
  )
}
