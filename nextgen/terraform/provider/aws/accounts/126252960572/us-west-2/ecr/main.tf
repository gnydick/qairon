provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

module "ecr" {
  source = "../../../../../../modules/aws/ecr"
  repos  = var.repos
}