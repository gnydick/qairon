provider "aws" {
  region="us-west-2"
  default_tags {
    tags = local.global_tags
  }
}

module "organization" {
  source = "../../../../../../modules/aws/organization"
  accounts = var.accounts
  global_maps = local.global_maps
  global_strings = local.global_strings
}