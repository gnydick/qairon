provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
//  version = "3.37.0"
}

module "vpcs" {
  for_each = var.vpc_configs
  source = "./vpc"
  vpc_config = var.vpc_configs[each.key]
  global_maps = local.global_maps
  global_strings = local.global_strings
  eks_configs = var.eks_configs
  nodegroup_configs = var.nodegroup_configs
  azs = var.azs
  public_subnets = var.public_subnets[each.key]
  private_subnets = var.private_subnets[each.key]
}