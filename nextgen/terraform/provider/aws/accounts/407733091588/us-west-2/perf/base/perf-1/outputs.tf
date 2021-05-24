output "nodes_security_group_id" {
  description = "Default Security group ID for all Worker Node groups in cluster"
  value       = module.cluster.nodes_security_group_id
}