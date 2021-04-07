provider "aws" {
  region = var.region
}

provider "template" {
}

data "template_file" "ark_user_policy" {
  template = file("${path.module}/ark/policy.json")
  vars = {
    bucketarn = aws_s3_bucket.bucket.arn
  }
}

resource "aws_s3_bucket" "bucket" {
  bucket = var.ark_bucket
  region = var.region
}

resource "aws_iam_user" "user" {
  name = var.ark_user
}

resource "aws_iam_user_policy" "user-policy" {
  user   = aws_iam_user.user.name
  policy = data.template_file.ark_user_policy.rendered
}

resource "aws_iam_access_key" "user-access-key" {
  user = aws_iam_user.user.name
}

output "access_key" {
  value = aws_iam_access_key.user-access-key.id
}

output "secret" {
  value = aws_iam_access_key.user-access-key.secret
}

