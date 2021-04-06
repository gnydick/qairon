module "vpc-infra-priv" {
  source = "../../../../../modules/route53_private_zone"
  config_name = "${var.config}"
  deployment_target = "${var.deployment_target}"
  environment = "${var.environment}"
  fqdn = "vpc.infra.priv"
  region = "${var.region}"
  vpc_id = "${data.aws_vpc.hosted_zone_vpc.id}"
}
module "vpc-metrics" {
  source = "../../../../../modules/route53_alias"
  name = "metrics"
  zone_id = "${module.vpc-infra-priv.zone_id}"
  identifier = "metrics"
  record = "${data.aws_elb.metrics.dns_name}"
  aws_hosted_zone_id = "${data.aws_elb_hosted_zone_id.elb_zone.id}"
}
