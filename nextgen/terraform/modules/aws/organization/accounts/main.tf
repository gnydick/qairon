
resource "aws_organizations_account" "account" {
  for_each = var.accounts
  name      = each.value.name
  email     = each.value.email
  role_name = each.value.role

  # There is no AWS Organizations API for reading role_name
  lifecycle {
    ignore_changes = [role_name]
  }
}