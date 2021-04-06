
resource "aws_security_group" "proxy_sg" {
  name = "${length(var.proxy_sg_name_override)==0?"${var.deployment_target}.stacks-proxy.sg":"${var.proxy_sg_name_override}"}"

  description = "proxy for cloudformation stacks so a stack can be deleted without having to break the sg links to other resources"
  vpc_id = "${var.vpc_id}"

  tags = "${merge(
                    map("Region", "${var.region}"),
                    map("Environment", "${var.environment}"),
                    map("Name","${var.deployment_target}.stacks-proxy.sg"),
                    map("Config","${var.config_name}"),
                    map("DeploymentTarget", "${var.deployment_target}"),
                    map("GeneratedBy", "terraform"),
                    "${var.extra_tags}")}"

}

resource "aws_security_group_rule" "same_group_egress" {
  lifecycle {
    prevent_destroy = true
  }
  source_security_group_id = "${aws_security_group.proxy_sg.id}"
  description = "hosts allowed to reach each other"

  from_port = 0
  protocol = "all"
  security_group_id = "${aws_security_group.proxy_sg.id}"
  to_port = 0
  type = "egress"
  depends_on = [
    "aws_security_group.proxy_sg"]
}

resource "aws_security_group_rule" "same_group_ingress" {
  lifecycle {
    prevent_destroy = true
  }
  source_security_group_id = "${aws_security_group.proxy_sg.id}"
  description = "hosts allowed to reach each other"

  from_port = 0
  protocol = "all"
  security_group_id = "${aws_security_group.proxy_sg.id}"
  to_port = 0
  type = "ingress"
  depends_on = [
    "aws_security_group.proxy_sg"]
}
