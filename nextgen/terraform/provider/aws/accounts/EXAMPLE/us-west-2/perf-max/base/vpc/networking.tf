 module "networking" {
   source = "../../../../../../../../modules/aws/networking"
   vpc_id = module.vpc.vpc_id
   public_subnet_cidr = var.public_subnets_cidr
   private_subnet_cidr = var.private_subnets_cidr
   azs = var.azs
   environment = var.environment
 }

