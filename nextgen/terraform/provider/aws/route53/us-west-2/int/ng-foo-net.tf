
module "ng-foo-net" {
  source = "../../../../../modules/route53_zone"
  config_name = "${var.config}"
  environment = "${var.environment}"
  fqdn = "ng.foo.net"
  region = "${var.region}"
}