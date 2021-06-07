module "vpc" {
  source         = "../../../../../../../modules/aws/vpc"
  vpc_config     = var.vpc_config
  global_maps    = var.global_maps
  global_strings = var.global_strings
}


