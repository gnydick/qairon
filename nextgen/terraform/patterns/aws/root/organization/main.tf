provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

module "organization" {
  source = "../../modules/aws/organization"
  global_maps = local.global_maps
  global_strings = local.global_strings
}


module "accounts" {
  for_each = var.accounts
  source = "../../modules/aws/accounts"
  account_tags = var.account_tags[each.key]
  email = each.value.email
  name = each.value.name
  role = each.value.role

}


module "sandbox-ou" {
  source = "./ou1"
  parent = module.organization.roots[0].id
}

module "security-ou" {
  source = "./ou2"
  parent = module.organization.roots[0].id

}

