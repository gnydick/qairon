output "private_subnets_ids" {
  value = module.private.private_subnets_ids
}

output "public_subnets_ids" {
  value = module.public.public_subnets_ids
}

#output "private_route_table_ids" {
#  value = aws_route_table.private.*.id
#}
#
#output "public_route_table_ids" {
#  value = aws_route_table.public.*.id
#}
