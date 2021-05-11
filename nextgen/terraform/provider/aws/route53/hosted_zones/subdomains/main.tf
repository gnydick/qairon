module "route53_hosted_zone" {
  count = length(var.zones)
  source = "../../../../../modules/aws/route53_zone"
  zone = "${element(var.zones, count.index )}.${var.parent_zone}"

  tier = "Public"
}