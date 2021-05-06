module "vpc" {
  source = "../../../../../../../../modules/aws/vpc"
  cidr = var.vpc_cidr
  name = var.name
  tags = var.tags
}

module "perf-1" {
  depends_on = [module.vpc]
  source = "./perf-1"
  environment = var.environment
  extra_tags = {}
  private_subnets = var.private_subnets["perf-1"]
  public_subnets = var.public_subnets["perf-1"]
  region = var.region
  vpc_id = module.vpc.vpc_id
  eks_version = var.eks_versions["perf-1"]
  cluster_log_retention_in_days = "90"
  azs = []
  cluster_egress_cidrs = []
  cluster_endpoint_public_access = false
  cluster_endpoint_public_access_cidrs = []
  cluster_number = var.number
  config = var.config
  name = var.name
}