locals {
  prefix = "${var.environment}.${var.deployment_target}.${var.region}"
}

resource "aws_lb" "nlb" {
  name               = var.name
  internal           = var.internal
  load_balancer_type = "network"
  security_groups    = var.security_groups
  subnets            = var.subnets

  enable_deletion_protection = var.deletion_protection

  enable_cross_zone_load_balancing = var.cross_zone

  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${local.prefix}.nlb"
    },
    {
      "DeploymentTarget" = var.deployment_target
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "Tier" = var.tier
    },
    var.extra_tags,
  )
}

