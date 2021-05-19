module "route53_hosted_zone" {
  for_each = var.zones
  source = "../../../../../modules/aws/route53_zone"
  zone = "${each.key}.${var.parent_zone}"
  tier = "Public"
}