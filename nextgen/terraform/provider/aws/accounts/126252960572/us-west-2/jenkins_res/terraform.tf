provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}




