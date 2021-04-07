module "example-dev1" {
  source           = "../reqeuster_mod"
  accepter-account = var.accepter-account["example-dev1"]
  accepter-cidr    = var.accepter-cidr["example-dev1"]
  accepter-sgs     = split(",", var.accepter-sgs["example-dev1"])
  accepter-vpc_id  = var.accepter-vpc_id["example-dev1"]
  config_name      = var.config_name

  environment      = var.environment
  region           = var.region
  requester_cidr   = var.requester_cidr
  requester_vpc    = var.requester_vpc
  requester_vpc_id = var.requester_vpc_id

  status        = var.status["example-dev1"]
  allow_dns_out = var.allow_dns_out
}

// only enable this after peering is setup
module "example-dev1-sgs" {
  source      = "../sg_mod"
  config_name = var.config_name

  environment = var.environment

  accepter-sgs = split(",", var.accepter-sgs["example-dev1"])

  requester_sgs = data.aws_security_groups.requester-sgs.ids
  status        = var.status["example-dev1"]

  requester_eks_sgs = var.requester_eks_sgs
}

