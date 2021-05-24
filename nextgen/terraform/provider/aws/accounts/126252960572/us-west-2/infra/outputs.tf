output "vpc_ids" {
  value = tomap({
    for k, vpc_id in module.vpcs : k => vpc_id.vpc_id
  })
}

output "eks_node_sg_ids" {
  value = tomap({
  for k, vpc in module.vpcs : k => vpc.eks_node_sg_ids
  })
}


output "private_subnet_ids" {
  value = tomap({
    for k, vpc in module.vpcs : k => vpc.private_subnet_ids
  })
}

output "public_subnet_ids" {
  value = tomap({
    for k, vpc in module.vpcs : k => vpc.public_subnet_ids
  })
}

output "cluster_oidc_provider_arns" {
  value = tomap({
  for k, vpc in module.vpcs: k => vpc.cluster_oidc_provider_arns
  })
}

output "cluster_oidc_issuer_urls" {
  value = tomap({
  for k, vpc in module.vpcs: k => vpc.cluster_oidc_issuer_urls
  })
}

output "cluster_oidc_providers" {
  value = tomap({
  for k, cluster in module.vpcs: k => cluster.cluster_oidc_providers
  })
}