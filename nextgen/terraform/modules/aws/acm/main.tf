resource "aws_acm_certificate" "this" {
  domain_name               = var.domain_name
  validation_method         = var.validation_method
  subject_alternative_names = var.subject_alternative_names
  tags                      = var.tags

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "this" {
  count           = length(var.subject_alternative_names)
  zone_id         = var.zone_id
  ttl             = var.ttl
  allow_overwrite = true
  name            = lookup(aws_acm_certificate.this.domain_validation_options[count.index], "resource_record_name")
  type            = lookup(aws_acm_certificate.this.domain_validation_options[count.index], "resource_record_type")
  records         = [lookup(aws_acm_certificate.this.domain_validation_options[count.index], "resource_record_value")]
}
