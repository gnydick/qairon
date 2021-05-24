locals {
  bucket = "${var.bucket_prefix}.s3-bucket"
  logging_bucket = "${var.bucket_prefix}-logging.s3-bucket"
}

resource "aws_s3_bucket_public_access_block" "bucket" {
  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}

resource "aws_s3_bucket" "logging" {
  bucket = local.logging_bucket
  acl = "log-delivery-write"


tags = merge(
  var.tags,
  {
    "Name" = local.logging_bucket
  }
  )
}


resource "aws_s3_bucket" "bucket" {
  bucket = local.bucket
  acl    = var.s3_acl

  logging {
    target_bucket = aws_s3_bucket.logging.id
    target_prefix = "log/"
  }


  tags = merge(
    var.tags,
    {
      "Name" = local.bucket
    }
  )
}

