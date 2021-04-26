provider "aws" {
  region = var.region
}


module "tfstate_s3_bucket" {
  source = "../../../../../../../modules/aws/s3_bucket"
  region = var.region

  config_tag = var.config_tag
  environment = var.environment
  name = "tfstate"
  role = ""
  s3_acl = "private"
  org = var.org
}


module "tfstate_dyndb_lock" {
  source = "../../../../../../../modules/aws/dynamodb_table"
  billing_mode = var.billing_mode
  config_tag = var.config_tag
  environment = var.environment
  name = var.tflock_dynamodb_table_name
  org = var.org
  region = var.region
  role = var.role
  stream_enabled = var.stream_enabled
  stream_view_type = var.stream_view_type
  hash_key = var.tflock_dynamodb_hash_key
  hash_key_type = var.tflock_dynamodb_hash_key_type
  write_capacity = var.tflock_dynamodb_write_capacity
}