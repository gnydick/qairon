//module "proxy_sg" {
//  source = "../../../../../../../../modules/aws/eks-security-group"
//  vpc_id = var.vpc_id
//
//  name = format("proxy-%s-%s.sg", var.global_strings.regional_prefix, var.eks_config.cluster_name)
//  global_maps = var.global_maps
//  global_strings = var.global_strings
//}


module "stack" {
  for_each = var.nodegroup_configs
  source                                   = "../../../../../../../../modules/aws/cloudformation"
  vpc_id                                   = var.vpc_id
  cp_sg_id                                 = module.cluster.cluster_security_group_id
  subnets                                  = join(",", module.networking.private_subnets_ids)
  name = each.key
  cluster_name = var.eks_config.cluster_name
  nodegroup_config = var.nodegroup_configs[each.key]
  global_maps = var.global_maps
  global_strings = var.global_strings
}




//module "svcs-foo_svcs-peering" {
//  source           = "../../../../../../../../modules/aws/nodegroup-pair-sgs"
//  nodegroup_a_id   = module.svcs_stack.security_group_id
//  nodegroup_b_id   = module.lowpri_svcs_stack.security_group_id
//  nodegroup_a_name = module.svcs_stack.nodegroup_name
//  nodegroup_b_name = module.lowpri_svcs_stack.nodegroup_name
//}

