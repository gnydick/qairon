output "private_subnets_ids" {
  description = "List of IDs of private subnets"
  value       = concat(aws_subnet.private.*.id, [""])[0]
}