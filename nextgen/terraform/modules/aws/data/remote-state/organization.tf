
data "terraform_remote_state" "organization" {
  backend = "s3"

  config = {
    profile = var.aws_provider_profile_name
    key     = "root/organization"
    bucket  = "terraform-state-backend-${data.aws_caller_identity.core-lib.account_id}.s3-bucket"
    region  = var.tfstate_region
  }
}



