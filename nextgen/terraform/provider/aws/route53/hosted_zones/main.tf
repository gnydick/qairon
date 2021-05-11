provider "aws" {
  region="us-west-2"
  default_tags {
    tags = local.global_tags
  }
}

module "route53_hosted_zone" {
  count = length(var.zones)
  source = "../../../../modules/aws/route53_zone"
  zone = element(var.zones, count.index)
  tier = "Public"
}

module "subdomains" {
  count = length(var.zones)
  source = "./subdomains"
  tier = "Public"
  zones = lookup(var.subdomains, element(var.zones, count.index))
  parent_zone = element(var.zones,count.index )
}