data "aws_caller_identity" "current" {}

module "cluster" {
  source             = "../../../../../../../../modules/aws/eks"
  eks_version        = 1.19
  azs                = var.azs
  region             = var.region
  environment        = var.environment
#  config_name        = var.config_name
  vpc_id             = var.vpc_id
  private_subnets_ids = var.private_subnets_ids
  public_subnets_ids  = var.public_subnets_ids
#  deployment_target  = var.deployment_target
  cluster_name       = var.environment
  cluster_log_retention_in_days = var.cluster_log_retention_in_days
  cluster_iam_role_name = format("%s-EKS-cluster-role", var.environment)
  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  cluster_egress_cidrs = var.cluster_egress_cidrs
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
}