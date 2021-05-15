provider "aws" {
  region="us-west-2"
  default_tags {
    tags = local.global_tags
  }
}


module "tfstate_s3_bucket" {
  source = "../../../../../../modules/aws/s3_bucket"
  org = var.org
  config = var.config
  environment = var.environment
  s3_acl = "private"
  dept = "services"
  bucket_prefix = "terraform-state-backend-981861990024"
  tags = local.global_tags
}


module "tfstate_dyndb_lock" {
  source = "../../../../../../modules/aws/dynamodb_table"
  billing_mode = var.billing_mode
  config = var.config
  environment = var.environment
  table_prefix = "${local.regional_prefix}-${data.aws_caller_identity.core-lib.account_id}"
  org = var.org
  region = var.region
  stream_enabled = var.stream_enabled
  stream_view_type = var.stream_view_type
  hash_key = "LockID"
  hash_key_type = "S"
  write_capacity = 0
  dept = var.dept
  tags = local.global_tags
  pit_recovery = true
}