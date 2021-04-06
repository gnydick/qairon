resource "aws_cloudfront_origin_access_identity" "origin_access_identity" {
  comment = "identity for S3"
}

resource "aws_cloudfront_distribution" "this" {
  origin {
    domain_name = aws_s3_bucket.this.bucket_regional_domain_name
    origin_id   = var.cdn_bucket_name
    origin_path = var.origin_path

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.origin_access_identity.cloudfront_access_identity_path
      }
  }

  enabled             = var.cdn_enabled
  is_ipv6_enabled     = var.cdn_ipv6_enabled
  default_root_object = "index.html"
  aliases = var.cdn_alias
  price_class = var.price_class

  logging_config {
    include_cookies = var.log_include_cookies
    bucket          = "${var.log_bucket}.s3.amazonaws.com"
    prefix          = var.log_prefix
  }

  default_cache_behavior {
    allowed_methods  = var.allowed_methods
    cached_methods   = var.cached_methods
    target_origin_id = var.cdn_bucket_name
    viewer_protocol_policy = var.viewer_protocol_policy
    forwarded_values {
      query_string = var.query_string_enabled
      cookies {
        forward = "none"
      }
    }
    min_ttl                = var.min_ttl
    default_ttl            = var.default_ttl
    max_ttl                = var.max_ttl
  }
  restrictions {
    geo_restriction {
      restriction_type = var.restriction_type
      locations        = var.locations
    }
  }
  tags = {
    CostCenter = var.cost_center
    Environment = var.environment
    terraform_managed = "true"
    managed_by = "terraform"
  }
  viewer_certificate {
      ssl_support_method = var.ssl_support_method
      acm_certificate_arn = var.acm_certificate_arn
      minimum_protocol_version = var.minimum_protocol_version
    }
  }
