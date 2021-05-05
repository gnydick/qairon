output "id" {
  value       = aws_acm_certificate.this.id
  description = "The ID of the certificate"
}

output "arn" {
  value       = aws_acm_certificate.this.arn
  description = "The ARN of the certificate"
}

output "domain_validation_options" {
  value       = aws_acm_certificate.this.domain_validation_options
  description = "CNAME records that are added to the DNS zone to complete certificate validation"
}
