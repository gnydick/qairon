resource "aws_security_group" "control_group" {
  vpc_id = var.vpc_id
  tags = {
    Region           = var.region
    Environment      = var.environment
    Name             = "cp.${var.environment}${var.cluster_number}.${var.region}.eks.security_group"
    Config           = var.config_name
    GeneratedBy      = "terraform"
    DeploymentTarget = var.deployment_target
  }
}

