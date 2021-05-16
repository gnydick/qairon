provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

module "vpcs" {
  count = length(keys(var.structure))
  source = "./vpc"
  environment = var.environment
  region = var.region
  azs = var.azs
  map_public_ip_on_launch = lookup(var.map_public_ip_on_launch, element(keys(var.structure), count.index))
  private_subnet_suffix = ""
  private_subnet_tags = {}
  private_subnets = lookup(var.private_subnets, element(keys(var.structure), count.index))
  public_subnet_suffix = ""
  public_subnet_tags = {}
  public_subnets = lookup(var.public_subnets, element(keys(var.structure), count.index))
  tags = local.global_tags
  vpc_cidr = lookup(var.vpc_cidrs, element(keys(var.structure), count.index))
  name = "${local.global_prefix}-${element(keys(var.structure), count.index)}"
  config = var.config
  eks_versions = lookup(var.eks_versions, element(keys(var.structure), count.index))
  number = count.index
  cluster_endpoint_public_access = lookup(var.cluster_endpoint_public_access, element(keys(var.structure), count.index))
  global_prefix = local.global_prefix
  regional_prefix = local.regional_prefix
  cluster_enabled_log_types = lookup(var.cluster_enabled_log_types, element(keys(var.structure), count.index))
  eks_targets = lookup(var.structure, element(keys(var.structure), count.index))
  global_maps = local.global_maps
  global_strings = local.global_strings
}