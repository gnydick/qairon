data "terraform_remote_state" "vpc" {
  backend = "s3"

  config = {
    key    = format("%s/infra", var.region)
    bucket = format("terraform-state-backend-%s.s3-bucket", data.aws_caller_identity.core-lib.account_id)
    region = var.tfstate_region
  }
}

