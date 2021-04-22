output "private_subnet_ids" {
  value = [
    module.private.private_subnet_ids,
  ]
}

output "public_subnet_ids" {
  value = [
    module.public.public_subnet_ids,
  ]
}

output "private_route_table_ids" {
  value = aws_route_table.private.*.id
}

output "public_route_table_ids" {
  value = aws_route_table.public.*.id
}
