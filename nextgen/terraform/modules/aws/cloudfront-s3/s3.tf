data "aws_iam_policy_document" "s3_cdn_policy" {
  statement {
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = ["${aws_s3_bucket.this.arn}/*", "${aws_s3_bucket.this.arn}" ]

    principals {
      type        = "AWS"
      identifiers = ["${aws_cloudfront_origin_access_identity.origin_access_identity.iam_arn}"]
    }
  }
}

resource "aws_s3_bucket_policy" "this" {
  bucket = aws_s3_bucket.this.id
  policy = data.aws_iam_policy_document.s3_cdn_policy.json
}

resource "aws_s3_bucket" "this" {
  bucket        = var.cdn_bucket_name
  acl           = "private"
  tags = {
    CostCenter = var.cost_center
    Stack      = var.environment
    terraform_managed = "true"
    managed_by = "terraform"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "logs" {
  bucket        = var.log_bucket
  acl           = "private"
  tags = {
    CostCenter = var.cost_center
    Stack      = var.environment
    terraform_managed = "true"
    managed_by = "terraform"
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm     = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket = aws_s3_bucket.logs.id

  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}
