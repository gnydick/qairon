
resource "aws_route53_record" "alias" {


  name = var.name
  type = "A"
  zone_id = var.zone_id


  alias {
    evaluate_target_health = false
    name = var.record
    zone_id = var.aws_hosted_zone_id
  }
}