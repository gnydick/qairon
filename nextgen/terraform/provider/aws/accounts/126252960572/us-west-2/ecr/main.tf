provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

module "ecr" {
  source = "../../../../../../modules/aws/ecr"
  repos  = var.repos
  principal_identifiers = var.principal_identifiers
  account_id = data.aws_caller_identity.core-lib.account_id
  region = var.region
}