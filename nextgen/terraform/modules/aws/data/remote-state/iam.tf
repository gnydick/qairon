data "terraform_remote_state" "iam" {
  backend = "s3"

  config = {
    profile = var.aws_provider_profile_name
    key     = "iam/terraform.tfstate"
    bucket  = "${var.tf_remote_state_s3_bucket_prefix}-${data.aws_caller_identity.core-lib.account_id}-${var.environment}"
    region  = var.tf_remote_state_s3_bucket_current_environment_region
  }
}