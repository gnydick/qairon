module "vpc" {
  source = "../../../../../../../../modules/aws/vpc"
  cidr = var.vpc_cidr
  name = "${var.region}-${var.environment}"
  tags = {
    "Region" = var.region
    "Environment" = var.environment
    "GeneratedBy" = "terraform"
  }
}
