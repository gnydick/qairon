resource "aws_acm_certificate" "cert" {
  domain_name       = var.fqdn
  validation_method = "DNS"
  tags = merge(
    {
      "Region" = var.region
    },
    {
      "Environment" = var.environment
    },
    {
      "Name" = "${var.fqdn}.cert"
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
    create_before_destroy = true
  }
}

