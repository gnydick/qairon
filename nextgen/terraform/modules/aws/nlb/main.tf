
locals {
  prefix = "${var.environment}.${var.deployment_target}.${var.region}"
}


resource "aws_lb" "nlb" {
  name = "${var.name}"
  internal = "${var.internal}"
  load_balancer_type = "network"
  security_groups = ["${var.security_groups}"]
  subnets = ["${var.subnets}"]

  enable_deletion_protection = "${var.deletion_protection}"

  enable_cross_zone_load_balancing = "${var.cross_zone}"

  tags = "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${local.prefix}.nlb"),
                    map("DeploymentTarget","${var.deployment_target}"),
                    map("Config","${var.config_name}"),
                    map("GeneratedBy", "terraform"),
                    map("Tier", "${var.tier}"),
                    "${var.extra_tags}")}"


}