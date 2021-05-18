output "private_subnets_ids" {
  value = aws_subnet.private.*.id
}

output "public_subnets_ids" {
  value = aws_subnet.public.*.id
}

output "private_route_table_ids" {
  value = aws_route_table.private_rt.*.id
}

output "public_route_table_ids" {
  value = aws_route_table.public_rt.*.id
}
