//locals {
//  key_name = "${var.region}-${var.key_name}"
//}
//
//module "hipri_svcs_stack" {
//  source                                   = "../../../../../../../../modules/aws/cloudformation"
//  azs                                      = var.azs
//  ami                                      = var.hipri_nodegroup_ami
//  vpc_id                                   = var.vpc_id
//  config_name                              = var.config_name
//  key_name                                 = local.key_name
//  cp_sg_id                                 = var.cp_sg_id
//  region                                   = var.region
//  role                                     = "hiprisvcs"
//  environment                              = var.environment
//  node_volume_size                         = var.node_volume_size
//  extra_tags                               = {}
//  node_instance_type                       = var.hipri_instance_type
//  subnets                                  = join(",", var.private_subnet_ids)
//  node_auto_scaling_group_desired_capacity = var.hipri_scaling_desired_capacity
//  group_number                             = "1"
//  min_size                                 = var.hipri_min_size
//  max_size                                 = var.hipri_max_size
//  bootstrap_arguments                      = var.hipri_bootstrap_arguments
//  deployment_target                        = var.deployment_target
//  cluster_name                             = module.cluster.cluster_name
//  nodegroup_number                         = var.nodegroup_number
//  proxy_security_group                     = module.proxy_sg.sg_id
//}
//
//
//module "lowpri_svcs_stack" {
//  source                                   = "../../../../../../../../modules/aws/cloudformation"
//  azs                                      = var.azs
//  ami                                      = var.lowpri_nodegroup_ami
//  vpc_id                                   = var.vpc_id
//  config_name                              = var.config_name
//  key_name                                 = local.key_name
//  cp_sg_id                                 = var.cp_sg_id
//  region                                   = var.region
//  role                                     = "lowprisvcs"
//  environment                              = var.environment
//  node_volume_size                         = var.node_volume_size
//  extra_tags                               = {}
//  node_instance_type                       = var.lowpri_instance_type
//  subnets                                  = join(",", var.private_subnet_ids)
//  node_auto_scaling_group_desired_capacity = var.lowpri_scaling_desired_capacity
//  group_number                             = "1"
//  min_size                                 = var.lowpri_min_size
//  max_size                                 = var.lowpri_max_size
//  bootstrap_arguments                      = var.lowpri_bootstrap_arguments
//  deployment_target                        = var.deployment_target
//  cluster_name                             = module.cluster.cluster_name
//  nodegroup_number                         = var.nodegroup_number
//  proxy_security_group                     = module.proxy_sg.sg_id
//}
//
//
//module "hipri_svcs-foo_svcs-peering" {
//  source           = "../../../../../../../../modules/aws/nodegroup-pair-sgs"
//  nodegroup_a_id   = module.hipri_svcs_stack.security_group_id
//  nodegroup_b_id   = module.lowpri_svcs_stack.security_group_id
//  nodegroup_a_name = module.hipri_svcs_stack.nodegroup_name
//  nodegroup_b_name = module.lowpri_svcs_stack.nodegroup_name
//}
//
