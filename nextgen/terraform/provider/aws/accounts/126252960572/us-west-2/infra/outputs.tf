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

