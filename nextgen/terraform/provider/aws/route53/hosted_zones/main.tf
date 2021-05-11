provider "aws" {
  region="us-west-2"
  default_tags {
    tags = local.global_tags
  }
}

module "route53_hosted_zone" {
  source = "../../../../modules/aws/route53_zone"
  zones = var.zones
  config_name = var.config
  environment = var.environment
  tier = "Public"
}