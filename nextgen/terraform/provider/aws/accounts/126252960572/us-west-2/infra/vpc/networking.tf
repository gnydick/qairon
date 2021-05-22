module "networking" {
   source = "../../../../../../../modules/aws/modular_networking"
   vpc_id = module.vpc.vpc_id
   public_subnet_cidrs = var.public_subnets
   private_subnet_cidrs = var.private_subnets
   azs = var.azs
   global_maps = var.global_maps
   global_strings = var.global_strings
}

