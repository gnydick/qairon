module "ou" {
  source = "../../../../../../../../modules/aws/ou"
  name = "Imvu"
  parent = var.parent
}

module "jgelin-ou" {
  source = "./jgelin"
  parent = module.ou.id
}

