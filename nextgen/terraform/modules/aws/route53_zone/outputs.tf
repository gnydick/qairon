output "zone_ids" {
  value = aws_route53_zone.zone.*.id
}

