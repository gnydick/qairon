module "networking" {
   source = "../../../../../../modules/aws/modular-networking/private_subnet"

   azs = var.azs
   global_maps = local.global_maps
   global_strings = local.global_strings
   private_subnet_cidrs = var.rds_subnets
   vpc_id = data.terraform_remote_state.vpc.outputs.vpc_ids["vpc1"]

}

