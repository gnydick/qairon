module "vpc" {
  source = "../../../../../../../modules/aws/vpc"
  vpc_config = var.vpc_config
  global_maps = var.global_maps
  global_strings = var.global_strings
}



module "eks_targets" {
  for_each = var.eks_configs[var.vpc_config.name]
  depends_on = [module.vpc]
  source = "./eks_target"
  eks_config = var.eks_configs[var.vpc_config.name][each.key]
  azs = var.azs
  vpc_id = module.vpc.vpc_id
  public_subnets = var.public_subnets[each.key]
  private_subnets = var.private_subnets[each.key]
  nodegroup_configs = var.nodegroup_configs[var.vpc_config.name][each.key]
  global_maps = var.global_maps
  global_strings = var.global_strings
}