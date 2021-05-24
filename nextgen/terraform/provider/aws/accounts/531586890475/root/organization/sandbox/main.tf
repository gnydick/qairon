module "ou" {
  source = "../../../../../../../modules/aws/ou"
  name = "Sandbox"
  parent = var.parent
  tags = {
    "Org" = "togetherlabs",
    "Dept" = "it"
  }
}
