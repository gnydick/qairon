resource "aws_route53_record" "record" {
  name = "${var.name}"
  type = "${var.type}"
  zone_id = "${var.zone_id}"
}