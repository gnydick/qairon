locals {
  bucket_perfix = "${var.org}-${data.aws_caller_identity.current.account_id}-${var.environment}"
}

module "s3-content-manager" {
  source = "../../../../../../../../modules/aws/s3_bucket"
  bucket_prefix = "${local.bucket_perfix}-content-manager"
  config = "default"
  dept = "services"
  environment = var.environment
  org = var.org
  s3_acl = "private"
  tags = {
    Environment = var.environment,
    GeneratedBy = "terraform"
  }
}