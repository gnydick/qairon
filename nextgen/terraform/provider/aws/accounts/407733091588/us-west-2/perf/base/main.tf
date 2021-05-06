provider "aws" {
  region = var.region
}



module "vpc-1" {
  source = "./vpc-1"
  environment = var.environment
  region = var.region
  azs = var.azs
  map_public_ip_on_launch = false
  private_subnet_suffix = ""
  private_subnet_tags = {}
  private_subnets = values(var.private_subnets["vpc-1"])
  public_subnet_suffix = ""
  public_subnet_tags = {}
  public_subnets = values(var.public_subnets["vpc-1"])
  tags = local.global_tags
  vpc_cidr = var.vpc_cidr["vpc-1"]
  name = local.global_prefix
  config = var.config
  eks_versions = var.eks_versions["vpc-1"]
  number = "1"
}

