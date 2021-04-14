locals {
  cluster_name = var.deployment_target
}

module "cluster" {
  source             = "../../../../../../../modules/aws/eks"
  eks_version        = 1.12
  azs                = var.azs
  key_name           = var.key_name
  region             = var.region
  vpc_cidr           = var.vpc_cidr
  environment        = var.environment
  config_name        = var.config_name
  vpc_id             = var.vpc_id
  private_subnet_ids = var.private_subnet_ids
  public_subnet_ids  = var.public_subnet_ids
  deployment_target  = var.deployment_target
  cluster_name       = local.cluster_name
}

//
//module "vpn" {
//  source = "openvpn"
//  key_name = "${var.key_name}"
//  environment = "${var.environment}"
//  extra_tags = {}
//  region = "${var.region}"
//  vpc_id = "${var.vpc_id}"
//  config_name = "${var.config_name}"
//  deployment_target = "${var.deployment_target}"
//  tier = "external"
//}

module "proxy_sg" {
  source            = "../../../../../../../modules/aws/eks-security-group"
  cluster_number    = var.cluster_number["perf-1"]
  config_name       = var.config_name
  deployment_target = var.deployment_target
  environment       = var.environment
  extra_tags = merge(
    var.extra_tags,
    {
      "Role" = "proxy"
    },
  )
  region = var.region
  vpc_id = var.vpc_id
}

module "roles" {
  source      = "./roles"
  clustername = local.cluster_name
  environment = var.environment
}

