module "organization" {
  source = "../../../../../../../modules/aws/organization"
  email = var.email
  name = var.org_name
  organization_role = var.org_role
  region = var.region
}