data "terraform_remote_state" "vpc" {
  backend = "s3"

  config = {
    //    profile = var.aws_provider_profile_name
    key    = format("%s/%s", var.region, var.environment)
    bucket = format("terraform-state-backend-%s.s3-bucket", data.aws_caller_identity.core-lib.account_id)
    region = var.tfstate_region
  }
}

