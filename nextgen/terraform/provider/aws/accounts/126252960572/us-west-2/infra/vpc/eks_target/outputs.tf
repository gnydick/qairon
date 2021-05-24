output "eks_node_sg" {

  value = module.cluster.nodes_security_group_id
}

output "cluster_oidc_provider_arn" {
  value = module.cluster.cluster_oidc_provider_arn
}

output "cluster_oidc_issuer_url" {
  value = module.cluster.cluster_oidc_issuer_url
}

output "cluster_oidc_providers" {
  value = module.cluster.cluster_oidc_provider
}