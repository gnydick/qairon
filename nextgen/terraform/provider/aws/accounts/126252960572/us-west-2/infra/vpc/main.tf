module "vpc" {
  source = "../../../../../../../modules/aws/vpc"
  cidr = var.vpc_cidr
  name = var.name
  tags = var.tags

  global_maps = var.global_maps
  global_strings = var.global_strings
}



module "eks_targets" {
  for_each = var.eks_targets
  depends_on = [module.vpc]
  source = "./eks_target"
  environment = var.environment
  extra_tags = {}
  private_subnets = lookup(var.private_subnets, each.key)
  public_subnets = lookup(var.public_subnets, each.key)
  region = var.region
  vpc_id = module.vpc.vpc_id
  eks_version = var.eks_versions[each.key]
  cluster_log_retention_in_days = "90"
  azs = var.azs
  cluster_egress_cidrs = []
  cluster_endpoint_public_access = lookup(var.cluster_endpoint_public_access, each.key)
  cluster_endpoint_public_access_cidrs = []
  config = var.config
  name = each.key
  cluster_enabled_log_types = lookup(var.cluster_enabled_log_types, each.key)
  map_public_ip_on_launch = lookup(var.map_public_ip_on_launch, each.key)
  global_maps = var.global_maps
  global_strings = var.global_strings
}