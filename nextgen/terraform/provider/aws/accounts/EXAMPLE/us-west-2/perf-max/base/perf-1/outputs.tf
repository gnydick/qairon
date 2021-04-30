output "cluster_name" {
  description = "Name of the EKS Cluster"
  value = module.cluster.cluster_name
}

output "cluster_arn" {
  description = "The Amazon Resource Name (ARN) of the cluster."
  value       = module.cluster.cluster_arn
}

output "cluster_endpoint" {
  description = "The endpoint for your EKS Kubernetes API."
  value       = module.cluster.cluster_endpoint
}

output "cluster_version" {
  description = "The Kubernetes server version for the EKS cluster."
  value       = module.cluster.cluster_version
}

output "cluster_iam_role_name" {
  description = "IAM role name of the EKS cluster."
  value       = module.cluster.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN of the EKS cluster."
  value       = module.cluster.cluster_iam_role_arn
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster. On 1.14 or later, this is the 'Additional security groups' in the EKS console."
  value       = module.cluster.cluster_security_group_id
}

output "nodes_security_group_id" {
  description = "Default Security group ID for all Worker Node groups in cluster"
  value = module.cluster.nodes_security_group_id
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster OIDC Issuer"
  value       = module.cluster.cluster_oidc_issuer_url
}