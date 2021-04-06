
resource "aws_route53_zone" "env" {
  vpc_region = "${var.region}"
  name       = "${var.environment}.${var.region}.priv"
  vpc_id     = "${var.vpc_id}"

  tags {
    Region = "${var.region}"
    GeneratedBy = "terraform"
    Name        = "${var.environment}.${var.region}.priv"
    Environment = "${var.environment}"
    DeploymentTarget = "${var.deployment_target}"
    "kubernetes.io/cluster/prod1-us-west-2"     = "owned"
  }
}
