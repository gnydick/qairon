terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-464431486678.s3-bucket"
    key            = "us-west-2/prod"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-prod-us-west-2-tfstate-sandbox-464431486678.dynamodb-table"
  }
}
