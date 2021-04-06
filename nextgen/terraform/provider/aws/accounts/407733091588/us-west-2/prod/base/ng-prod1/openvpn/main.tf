resource "aws_route53_record" "ng-prod1-vpn" {

  name = "ng-prod1.vpn"
  type = "CNAME"
  zone_id = "${data.aws_route53_zone.infra.zone_id}"
  records = ["${data.aws_elb.elb.dns_name}"]
  ttl = 60

}


