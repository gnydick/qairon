locals {
  bucket = "${var.bucket_prefix}.s3-bucket"
}

resource "aws_s3_bucket_public_access_block" "bucket" {
  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

}
resource "aws_s3_bucket" "bucket" {
  bucket = local.bucket
  acl    = var.s3_acl


  tags = merge(
    var.tags,
    {
      "Name" = local.bucket
    }
  )
}

