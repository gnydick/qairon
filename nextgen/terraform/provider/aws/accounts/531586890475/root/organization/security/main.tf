module "ou" {
  source = "../../../../../../../modules/aws/ou"
  name = "Security"
  parent = var.parent
  tags = {
    "Org" = "togetherlabs",
    "Dept" = "it"
  }
}