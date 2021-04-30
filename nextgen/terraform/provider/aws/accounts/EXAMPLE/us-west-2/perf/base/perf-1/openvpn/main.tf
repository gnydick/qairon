resource "aws_route53_record" "perf-1-vpn" {

  name = "perf-1.vpn"
  type = "CNAME"
  zone_id = "${data.aws_route53_zone.infra.zone_id}"
  records = ["${data.aws_elb.elb.dns_name}"]
  ttl = 60

}


