module "ou" {
  source = "../../../../../../../modules/aws/ou"
  name = "All"
  parent = var.parent
  tags = {
    "Org" = "togetherlabs",
    "Dept" = "it"
  }
}
