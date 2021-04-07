provider "aws" {
}

module "example-stage1" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  requesting-cidr = "${lookup(var.requesting-cidr,"example-stage1")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"example-stage1")}"
  req-sgs = "${lookup(var.req-sgs,"example-stage1")}"
  status = "${lookup(var.status,"example-stage1")}"
  allow_dns_in = "${lookup(var.status,"example-stage1")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "example-stage1")}"
}


module "example-stage1-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"example-stage1"))}"
  status = "${lookup(var.status,"example-stage1")}"
  region = "${var.region}"
}


module "example-prod1" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  requesting-cidr = "${lookup(var.requesting-cidr,"example-prod1")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"example-prod1")}"
  req-sgs = "${lookup(var.req-sgs,"example-prod1")}"
  status = "${lookup(var.status,"example-prod1")}"
  allow_dns_in = "${lookup(var.status,"example-prod1")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "example-prod1")}"
}


module "example-prod1-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"example-prod1"))}"
  status = "${lookup(var.status,"example-prod1")}"
  region = "${var.region}"
}


module "example-dev2" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  requesting-cidr = "${lookup(var.requesting-cidr,"example-dev2")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"example-dev2")}"
  req-sgs = "${lookup(var.req-sgs,"example-dev2")}"
  status = "${lookup(var.status,"example-dev2")}"
  allow_dns_in = "${lookup(var.status,"example-dev2")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "example-dev2")}"
}


module "example-dev2-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"
  

  req-sgs = "${split(",",lookup(var.req-sgs,"example-dev2"))}"
  status = "${lookup(var.status,"example-dev2")}"
  region = "${var.region}"
}


module "example-dev1" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  
  requesting-cidr = "${lookup(var.requesting-cidr,"example-dev1")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"example-dev1")}"
  req-sgs = "${lookup(var.req-sgs,"example-dev1")}"
  status = "${lookup(var.status,"example-dev1")}"
  allow_dns_in = "${lookup(var.status,"example-dev1")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "example-dev1")}"
}


module "example-dev1-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"example-dev1"))}"
  status = "${lookup(var.status,"example-dev1")}"
  region = "${var.region}"
}

module "example-dev1-new" {
  source = "../accepter_mod"
  accepter-vpc_id = "${var.accepting-vpc_id}"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"

  requesting-cidr = "${lookup(var.requesting-cidr,"example-dev1-new")}"
  requesting-vpc_id = "${lookup(var.requesting-vpc_id,"example-dev1-new")}"
  req-sgs = "${lookup(var.req-sgs,"example-dev1-new")}"
  status = "${lookup(var.status,"example-dev1-new")}"
  allow_dns_in = "${lookup(var.status,"example-dev1-new")=="active"?var.allow_dns_in:false}"
  requester_account = "${lookup(var.requester_account, "example-dev1-new")}"
}


module "example-dev1-new-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.sg_environment}"

  req-sgs = "${split(",",lookup(var.req-sgs,"example-dev1-new"))}"
  status = "${lookup(var.status,"example-dev1-new")}"
  region = "${var.region}"
}
