
data "aws_route53_zone" "this" {
  name         = var.domain
}

resource "aws_route53_record" "ipv4" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.route53_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.this.domain_name
    zone_id                = aws_cloudfront_distribution.this.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "ipv6" {
  zone_id = data.aws_route53_zone.this.zone_id
  name    = var.route53_name
  type    = "AAAA"

  alias {
    name                   = aws_cloudfront_distribution.this.domain_name
    zone_id                = aws_cloudfront_distribution.this.hosted_zone_id
    evaluate_target_health = false
  }
}
