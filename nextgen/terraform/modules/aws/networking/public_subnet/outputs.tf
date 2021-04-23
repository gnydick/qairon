output "public_subnets_ids" {
  description = "List of IDs of public subnets"
  value       = concat(aws_subnet.public.*.id, [""])[0]
}