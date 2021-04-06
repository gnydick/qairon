
resource "aws_route53_zone" "zone" {
  name = "${var.fqdn}"
  tags = "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${var.fqdn}.zone"),
                    map("Config","${var.config_name}"),
                    map("GeneratedBy", "terraform"),
                    "${var.extra_tags}")}"
  lifecycle {
    ignore_changes = ["vpc"]
  }


}