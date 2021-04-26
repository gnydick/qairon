locals {
  name = "${var.org}.${var.environment}.${var.region}.${var.name}.${var.config_tag}.dynamodb_table"
}


resource "aws_dynamodb_table" "dynamodb_table" {
  name             = local.name
  hash_key         = var.hash_key
  billing_mode     = var.billing_mode
  stream_enabled   = var.stream_enabled
  stream_view_type = var.stream_view_type
  write_capacity = var.write_capacity

  attribute {
    name = var.hash_key
    type = var.hash_key_type
  }

  replica {
    region_name = "us-east-2"
  }

  replica {
    region_name = "us-west-1"
  }
}