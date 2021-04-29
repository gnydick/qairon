locals {
  max_subnet_length = max(
  length(var.private_subnets),
  )
  nat_gateway_ips = split(
  ",",
  join(",", aws_eip.nat.*.id),
  )
  nat_gateway_count = var.one_nat_gateway_per_az ? length(var.azs) : local.max_subnet_length
}