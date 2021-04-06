provider "aws" {
}

module "ng-stage1" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  requesting-cidr = "${lookup(var.requesting-cidr,"ng-stage1")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"ng-stage1")}"
  req-sgs = "${lookup(var.req-sgs,"ng-stage1")}"
  status = "${lookup(var.status,"ng-stage1")}"
  allow_dns_in = "${lookup(var.status,"ng-stage1")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "ng-stage1")}"
}


module "ng-stage1-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"ng-stage1"))}"
  status = "${lookup(var.status,"ng-stage1")}"
  region = "${var.region}"
}


module "ng-prod1" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  requesting-cidr = "${lookup(var.requesting-cidr,"ng-prod1")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"ng-prod1")}"
  req-sgs = "${lookup(var.req-sgs,"ng-prod1")}"
  status = "${lookup(var.status,"ng-prod1")}"
  allow_dns_in = "${lookup(var.status,"ng-prod1")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "ng-prod1")}"
}


module "ng-prod1-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"ng-prod1"))}"
  status = "${lookup(var.status,"ng-prod1")}"
  region = "${var.region}"
}


module "ng-dev2" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  requesting-cidr = "${lookup(var.requesting-cidr,"ng-dev2")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"ng-dev2")}"
  req-sgs = "${lookup(var.req-sgs,"ng-dev2")}"
  status = "${lookup(var.status,"ng-dev2")}"
  allow_dns_in = "${lookup(var.status,"ng-dev2")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "ng-dev2")}"
}


module "ng-dev2-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"
  

  req-sgs = "${split(",",lookup(var.req-sgs,"ng-dev2"))}"
  status = "${lookup(var.status,"ng-dev2")}"
  region = "${var.region}"
}


module "leg-dev" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  
  requesting-cidr = "${lookup(var.requesting-cidr,"leg-dev")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"leg-dev")}"
  req-sgs = "${lookup(var.req-sgs,"leg-dev")}"
  status = "${lookup(var.status,"leg-dev")}"
  allow_dns_in = "${lookup(var.status,"leg-dev")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "leg-dev")}"
}


module "leg-dev-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"leg-dev"))}"
  status = "${lookup(var.status,"leg-dev")}"
  region = "${var.region}"
}

module "leg-dev-new" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"

  requesting-cidr = "${lookup(var.requesting-cidr,"leg-dev-new")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"leg-dev-new")}"
  req-sgs = "${lookup(var.req-sgs,"leg-dev-new")}"
  status = "${lookup(var.status,"leg-dev-new")}"
  allow_dns_in = "${lookup(var.status,"leg-dev-new")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "leg-dev-new")}"
}


module "leg-dev-new-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"leg-dev-new"))}"
  status = "${lookup(var.status,"leg-dev-new")}"
  region = "${var.region}"
}
