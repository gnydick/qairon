module "cluster" {
  source             = "../../../../../../../../modules/aws/eks"
  vpc_id             = var.vpc_id
  private_subnets_ids = var.private_subnets
  public_subnets_ids  = var.public_subnets
  eks_config = var.eks_config
  global_maps = var.global_maps
  global_strings = var.global_strings
}