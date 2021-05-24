module "stack" {
  for_each         = var.nodegroup_configs
  source           = "../../../../../../../../modules/aws/cloudformation"
  vpc_id           = var.vpc_id
  cp_sg_id         = module.cluster.cluster_security_group_id
  subnets          = join(",", var.private_subnets["eks_nodes"])
  name             = each.key
  cluster_name     = var.eks_config.cluster_name
  nodegroup_config = var.nodegroup_configs[each.key]
  global_maps      = var.global_maps
  global_strings   = var.global_strings
  shared_node_sg = module.cluster.nodes_security_group_id
}


