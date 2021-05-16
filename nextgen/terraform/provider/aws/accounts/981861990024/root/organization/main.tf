provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

module "organization" {
  source = "../../../../../../modules/aws/organization"
  global_maps = local.global_maps
  global_strings = local.global_strings
}


module "accounts" {
  for_each = var.accounts
  source = "../../../../../../modules/aws/accounts"
  account_tags = var.account_tags[each.key]
  email = each.value.email
  name = each.value.name
  role = each.value.role

}
//
module "top_level_ous" {
  for_each = var.top_level_ous
  source = "../../../../../../modules/aws/ou"
  name = each.value
  parent = module.organization.roots[0].id
}
//
//module "sub_ous" {
//  depends_on = [module.top_level_ous]
//  source = "../../../../../../modules/aws/ou"
//  ous = {}
//  root =
//}