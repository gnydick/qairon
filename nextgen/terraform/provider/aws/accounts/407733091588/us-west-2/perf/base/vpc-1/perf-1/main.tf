
module "cluster" {
  source             = "../../../../../../../../../modules/aws/eks"
  eks_version        = var.eks_version
  azs                = var.azs
  vpc_id             = var.vpc_id
  private_subnets_ids = module.networking.private_subnets_ids
  public_subnets_ids  = module.networking.public_subnets_ids
  cluster_name       = var.name
  cluster_log_retention_in_days = var.cluster_log_retention_in_days
  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  cluster_egress_cidrs = var.cluster_egress_cidrs
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access
}