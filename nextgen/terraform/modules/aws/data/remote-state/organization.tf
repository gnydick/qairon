
data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    profile = var.aws_provider_profile_name
    key     = var.fqk
    bucket  = "terraform-state-backend-${data.aws_caller_identity.core-lib.account_id}"
    region  = var.tfstate_region
  }
}



