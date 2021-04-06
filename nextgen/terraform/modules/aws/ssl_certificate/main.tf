resource "aws_acm_certificate" "cert" {
  domain_name = "${var.fqdn}"
  validation_method = "DNS"
  tags = "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${var.fqdn}.cert"),
                    map("Config","${var.config_name}"),
                    map("GeneratedBy", "terraform"),
                    "${var.extra_tags}")}"

  lifecycle {
    create_before_destroy = true
  }
}
