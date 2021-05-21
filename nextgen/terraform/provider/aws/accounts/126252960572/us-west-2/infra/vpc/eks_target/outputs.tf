output "eks_node_sg" {

  value = module.cluster.nodes_security_group_id
}
output "private_subnet_ids" {
  value = module.networking.private_subnets_ids
}

output "public_subnet_ids" {
  value = module.networking.public_subnets_ids
}