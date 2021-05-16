module "ou" {
  source = "../../../../../../../modules/aws/ou"
  name = "Sandbox"
  parent = var.parent
  tags = {
    "Org" = "imvu",
    "Dept" = "rnd"
  }
}

module "imvu-ou" {
  source = "./imvu"
  parent = module.ou.id
}

