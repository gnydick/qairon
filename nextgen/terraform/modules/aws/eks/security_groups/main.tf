

resource "aws_security_group" "control_group" {
  vpc_id = "${var.vpc_id}"
  tags {
    Region = "${var.region}"
    Environment = "${var.environment}"
    Name        = "${var.deployment_target}.cp.security_group"
    Config      = "${var.config_name}"
    GeneratedBy = "terraform"
    DeploymentTarget = "${var.deployment_target}"
  }
}




