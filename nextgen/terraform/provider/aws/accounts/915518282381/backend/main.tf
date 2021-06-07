provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

module "tfstate_s3_bucket" {
  source        = "../../../../../modules/aws/s3_bucket"
  s3_acl        = "private"
  bucket_prefix = "terraform-state-backend-915518282381"
  tags          = local.global_tags
}


module "tfstate_dyndb_lock" {
  source           = "../../../../../modules/aws/dynamodb_table"
  billing_mode     = var.billing_mode
  config           = var.config
  environment      = var.environment
  table_prefix     = "${local.regional_prefix}-${data.aws_caller_identity.core-lib.account_id}"
  org              = var.org
  region           = var.region
  stream_enabled   = var.stream_enabled
  stream_view_type = var.stream_view_type
  hash_key         = "LockID"
  hash_key_type    = "S"
  write_capacity   = 0
  dept             = var.dept
  tags             = local.global_tags
  pit_recovery     = true
}