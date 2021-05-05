resource "aws_route53_zone" "zone" {
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
    var.extra_tags,
  )

  lifecycle {
    ignore_changes = [vpc]
  }
}

