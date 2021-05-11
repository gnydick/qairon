resource "aws_route53_zone" "zone" {
  count = length(var.zones)
  name  = element(var.zones, count.index)
  tags =  {"Tier": var.tier}
}

