
resource "aws_organizations_account" "account" {
  name      = var.name
  email     = var.email
  role_name = var.role

  # There is no AWS Organizations API for reading role_name
  lifecycle {
    ignore_changes = [role_name]
  }

  tags = var.account_tags

}