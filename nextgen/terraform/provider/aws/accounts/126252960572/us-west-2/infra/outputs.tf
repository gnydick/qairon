output "vpc_ids" {
  value = tomap({
  for k, vpc_id in module.vpcs : k => vpc_id.vpc_id
  })
}
