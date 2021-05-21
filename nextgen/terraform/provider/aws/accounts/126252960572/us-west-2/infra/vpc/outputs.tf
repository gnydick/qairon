output "vpc_id" {
  description = "The ID of the VPC"
  value = module.vpc.vpc_id
}

output "eks_node_sg_ids" {
  value = tomap({
  for k, cluster in module.eks_targets : k => cluster.eks_node_sg
  })
}


//
//output "vpc_arn" {
//  description = "The ARN of the VPC"
//  value       = module.vpc.vpc_arn
//}
//
//output "vpc_cidr_block" {
//  description = "The CIDR block of the VPC"
//  value       = module.vpc.vpc_cidr_block
//}
//
//
//output "default_security_group_id" {
//  description = "The ID of the security group created by default on VPC creation"
//  value       = module.vpc.default_security_group_id
//}
//
//output "default_network_acl_id" {
//  description = "The ID of the default network ACL"
//  value       = module.vpc.default_network_acl_id
//}
//
//output "default_route_table_id" {
//  description = "The ID of the default route table"
//  value       = module.vpc.default_route_table_id
//}