
locals {
  name = "${var.table_prefix}.dynamodb-table"
}


resource "aws_dynamodb_table" "dynamodb_table" {
  name             = local.name
  hash_key         = var.hash_key
  billing_mode     = var.billing_mode
  stream_enabled   = var.stream_enabled
  stream_view_type = var.stream_view_type
  write_capacity   = var.write_capacity
  point_in_time_recovery {
    enabled = var.pit_recovery
  }

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

  tags = merge(
    var.tags,
    {
      "Name" = local.name
    }
  )
}