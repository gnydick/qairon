module "ou" {
  source = "../../../modules/aws/ou"
  name = local.name
  parent = var.parent
  tags = {}
}


