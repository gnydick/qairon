resource "aws_route53_zone" "zone" {
  name  = var.zone
  tags =  {"Tier": var.tier}
}

