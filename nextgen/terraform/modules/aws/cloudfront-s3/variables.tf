
variable "domain" {
  description = "base domain name"
}

variable "cost_center" {
  description = "cost center"
}

variable "price_class" {
  description = "hosted zone ID"
}

variable "viewer_protocol_policy" {
  description = "policy for viewer protocol"
}

variable "ssl_support_method" {
  description = "ssl support method"
}

variable "minimum_protocol_version" {
  description = "TLS / SSL versions"
}

variable "locations" {
  description = "ISO codes for geo countries to block or allow"
  type = list(string)
}

variable "cdn_bucket_name" {
    description = "CDN S3 bucket name"
}

variable "origin_path" {
  description = "origin path in S3 bucket"
}

variable "route53_name" {
  description = "Route 53 DNS name for CDN"
}

variable "cdn_ipv6_enabled" {
  description = "IPV6 enabled for CDN"
}

variable "cdn_enabled" {
  description = "CDN enabled"
}

variable "cdn_alias" {
  description = "CDN alias domain names"
  type = list(string)
}

variable "log_include_cookies" {
  description = "include cookies in logs"
}

variable "log_bucket" {
  description = "S3 bucket for logs"
}

variable "log_prefix" {
  description = "prefix for CDN logs in S3 bucket"
}

variable "allowed_methods" {
  description = "allowed methods"
  type = list(string)
}

variable "cached_methods" {
  description = "cached methods"
  type = list(string)
}

variable "query_string_enabled" {
  description = "query string enabled"
}

variable "min_ttl" {
  description = "min ttl"
}

variable "max_ttl" {
  description = "max ttl"
}

variable "default_ttl" {
  description = "default ttl"
}

variable "restriction_type" {
  description = "restriction type"
}

variable "environment" {
  description = "environment"
}

variable "acm_certificate_arn" {
  description = "ACM arn"
}
