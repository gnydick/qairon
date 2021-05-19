provider "aws" {
  region="us-west-2"
  default_tags {
    tags = local.global_tags
  }
}

module "route53_hosted_zone" {
  for_each = var.zones
  source = "../../../../modules/aws/route53_zone"
  zone = each.key
  tier = each.value["Tier"]
}

module "subdomains" {
  for_each = var.zones
  source = "./subdomains"
  tier = "Public"
  zones = lookup(var.subdomains, each.key)
  parent_zone = each.key
}