module "vpc" {
  source = "../../../../../../../../modules/aws/vpc"
  cidr = var.vpc_cidr
  name_prefix = var.regional_prefix
  tags = var.tags
  number = var.number
}



module "eks_targets" {
  count = length(var.eks_targets)
  depends_on = [module.vpc]
  source = "./eks_target"
  environment = var.environment
  extra_tags = {}
  private_subnets = lookup(var.private_subnets, element(var.eks_targets, count.index))
  public_subnets = lookup(var.public_subnets, element(var.eks_targets, count.index))
  region = var.region
  vpc_id = module.vpc.vpc_id
  eks_version = var.eks_versions["perf-1"]
  cluster_log_retention_in_days = "90"
  azs = var.azs
  cluster_egress_cidrs = []
  cluster_endpoint_public_access = lookup(var.cluster_endpoint_public_access, element(var.eks_targets, count.index))
  cluster_endpoint_public_access_cidrs = []
  cluster_number = var.number
  config = var.config
  name_prefix = var.regional_prefix
  name = element(var.eks_targets, count.index)
  cluster_enabled_log_types = lookup(var.cluster_enabled_log_types, element(var.eks_targets, count.index))
}