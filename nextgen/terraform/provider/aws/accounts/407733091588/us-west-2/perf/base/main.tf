provider "aws" {
  region = var.region
}

module "vpc" {
  source = "./vpc"
  environment = var.environment
  region = var.region
}

 module "perf-1" {
   source = "./perf-1"
#   config_name = var.config_name
   environment = var.environment
   extra_tags = {}
   private_subnets_ids = module.vpc.private_subnet_ids
   public_subnets_ids = module.vpc.public_subnet_ids
   region = var.region
   vpc_id = module.vpc.vpc_id
   eks_version = "1.19"
   cluster_log_retention_in_days = "90"
 }