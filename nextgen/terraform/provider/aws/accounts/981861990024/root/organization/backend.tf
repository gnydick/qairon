terraform {
  backend "s3" {
    bucket = "terraform-state-backend-981861990024.s3-bucket"
    key = "root/organization"
    region = "us-west-2"
    dynamodb_table = "${local.regional_prefix}-${data.aws_caller_identity.core-lib.account_id}.dynamodb-table""
  }
}
