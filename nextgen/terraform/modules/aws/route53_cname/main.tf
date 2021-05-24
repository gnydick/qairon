resource "aws_route53_record" "cname" {
  ttl     = "300"
  name    = var.name
  type    = "CNAME"
  zone_id = var.zone_id
  records = [
  var.record]
}