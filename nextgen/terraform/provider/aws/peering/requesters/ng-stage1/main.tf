module "ng-dev1" {
  source = "../reqeuster_mod"
  accepter-account = "${lookup(var.accepter-account, "ng-dev1")}"
  accepter-cidr = "${lookup(var.accepter-cidr, "ng-dev1") }"
  accepter-sgs = "${split(",",lookup(var.accepter-sgs,"ng-dev1"))}"
  accepter-vpc_id = "${lookup(var.accepter-vpc_id, "ng-dev1")}"
  config_name = "${var.config_name}"

  environment = "${var.environment}"
  region = "${var.region}"
  requester_cidr = "${var.requester_cidr}"
  requester_vpc = "${var.requester_vpc}"
  requester_vpc_id = "${var.requester_vpc_id}"

  status = "${lookup(var.status,"ng-dev1")}"
  allow_dns_out = "${var.allow_dns_out}"
}

// only enable this after peering is setup
module "ng-dev1-sgs" {
  source = "../sg_mod"
  config_name = "${var.config_name}"

  environment = "${var.environment}"
  accepter-sgs = "${split(",",lookup(var.accepter-sgs,"ng-dev1"))}"

  requester_sgs = "${data.aws_security_groups.requester-sgs.ids}"
  status = "${lookup(var.status,"ng-dev1")}"

  requester_eks_sgs = "${var.requester_eks_sgs}"
}

