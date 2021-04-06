resource "aws_route53_zone" "zone" {
  vpc {
    vpc_id = "${var.vpc_id}"
    vpc_region = "${var.region}"
  }
  name = "${var.fqdn}"
  tags = "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${var.fqdn}.zone"),
                    map("Config","${var.config_name}"),
                    map("GeneratedBy", "terraform"),
                    map("DeploymentTarget", "${var.deployment_target}"),
                    "${var.extra_tags}")}"


}