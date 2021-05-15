module "organization" {
  source = "../../../../../../modules/aws/organization"
  accounts = var.accounts
  region = var.region
}