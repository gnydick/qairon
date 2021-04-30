 module "networking" {
   source = "../../../../../../../../modules/aws/networking"
   vpc_id = module.vpc.vpc_id
   public_subnets = var.public_subnets
   private_subnets = var.private_subnets
   azs = var.azs
   environment = var.environment
 }

