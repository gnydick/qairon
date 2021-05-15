provider "aws" {
  region = var.region
}


module "vpcs" {
  for_each = var.structure
  source = "./vpc"
  environment = var.environment
  region = var.region
  azs = var.azs
  map_public_ip_on_launch = lookup(var.map_public_ip_on_launch, each.key)
  private_subnet_suffix = ""
  private_subnet_tags = {}
  private_subnets = lookup(var.private_subnets, each.key)
  public_subnet_suffix = ""
  public_subnet_tags = {}
  public_subnets = lookup(var.public_subnets, each.key)
  tags = local.regional_tags
  vpc_cidr = lookup(var.vpc_cidrs, each.key)
  name = each.key
  config = var.config
  eks_versions = lookup(var.eks_versions, each.key)
  cluster_endpoint_public_access = lookup(var.cluster_endpoint_public_access, each.key)
  cluster_enabled_log_types = lookup(var.cluster_enabled_log_types,each.key)
  eks_targets = lookup(var.structure, each.key)
  global_maps = local.global_maps
  global_strings = local.global_strings
}