data "terraform_remote_state" "networking-dr" {
  backend = "s3"

  config = {
    profile = var.aws_provider_profile_name
    key     = "networking/terraform.tfstate"
    bucket  = "${var.tf_remote_state_s3_bucket_prefix}-${data.aws_caller_identity.core-lib.account_id}-${var.environment}-dr"
    region  = var.vpc_dr_region
  }
}
