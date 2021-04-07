provider "aws" {
  region = var.region
}

provider "template" {
}

data "template_file" "cost_user_s3_policy" {
  template = file("${path.module}/cost_management/user_policy.json")
  vars = {
    bucket_arn = aws_s3_bucket.foo-aws-cost-and-usage.arn
  }
}

data "template_file" "cost_bucket_s3_policy" {
  template = file("${path.module}/cost_management/bucket_policy.json")
  vars = {
    bucket_arn     = aws_s3_bucket.foo-aws-cost-and-usage.arn
    cost_mgmt_user = aws_iam_user.cost-user.arn
  }
}

resource "aws_s3_bucket" "foo-aws-cost-and-usage" {
  bucket = var.cost_bucket
  region = var.region
}

resource "aws_iam_user" "cost-user" {
  name = var.cost_user
}

resource "aws_iam_user_policy" "foo-cost-mgmt-user-policy" {
  policy = data.template_file.cost_user_s3_policy.rendered
  user   = aws_iam_user.cost-user.name
}

resource "aws_s3_bucket_policy" "foo-bucket-policy" {
  policy = data.template_file.cost_bucket_s3_policy.rendered
  bucket = aws_s3_bucket.foo-aws-cost-and-usage.bucket
}

resource "aws_athena_database" "cost_db" {
  bucket = aws_s3_bucket.foo-aws-cost-and-usage.bucket
  name   = "cost_and_usage"
}

data "template_file" "create_table_query" {
  template = file("${path.module}/cost_management/create_table.ddl")
  vars = {
    bucket = aws_s3_bucket.foo-aws-cost-and-usage.bucket
  }
}

resource "aws_athena_named_query" "create_table" {
  database = aws_athena_database.cost_db.name
  name     = "create_table"
  query    = data.template_file.create_table_query.rendered
}

