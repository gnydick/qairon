output "eks_node_sg" {

  value = module.cluster.nodes_security_group_id
}
