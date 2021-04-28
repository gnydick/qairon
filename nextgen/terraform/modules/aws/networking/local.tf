locals {
  nat_gateway_ips = split(
  ",",
  join(",", aws_eip.nat.*.id),
  )
}