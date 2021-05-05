resource "aws_route53_zone" "env" {
  vpc {
    vpc_region = var.region
    vpc_id     = var.vpc_id
  }
  name = "${var.environment}.${var.region}.priv"

  tags = {
    Region                                  = var.region
    GeneratedBy                             = "terraform"
    Name                                    = "${var.environment}.${var.region}.priv"
    Environment                             = var.environment
    DeploymentTarget                        = var.deployment_target
    "kubernetes.io/cluster/prod1-us-west-2" = "owned"
  }
}

