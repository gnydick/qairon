resource "aws_route53_zone" "zone" {
  vpc {
    vpc_id     = var.vpc_id
    vpc_region = var.region
  }
  name = var.fqdn
  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${var.fqdn}.zone"
    },
    {
      "Config" = var.config_name
    },
    {
      "GeneratedBy" = "terraform"
    },
    {
      "DeploymentTarget" = var.deployment_target
    },
    var.extra_tags,
  )
}

