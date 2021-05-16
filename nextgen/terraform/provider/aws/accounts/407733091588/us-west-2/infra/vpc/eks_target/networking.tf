module "networking" {
<<<<<<< HEAD
<<<<<<< HEAD:nextgen/terraform/provider/aws/accounts/407733091588/us-west-2/infra/vpc/eks_target/networking.tf
   source = "../../../../../../../../../modules/aws/networking"
=======
   source = "../../../../../../../modules/aws/networking"
>>>>>>> eb2dda1ba89e7b3a1bfa4de8015ea445d7cb55b3:nextgen/terraform/provider/aws/accounts/296547766921/infra/vpc/eks_target/networking.tf
=======
   source = "../../../../../../../../../modules/aws/networking"
>>>>>>> eb2dda1ba89e7b3a1bfa4de8015ea445d7cb55b3
   vpc_id = var.vpc_id
   public_subnets = var.public_subnets
   private_subnets = var.private_subnets
   azs = var.azs
   environment = var.environment
 }

