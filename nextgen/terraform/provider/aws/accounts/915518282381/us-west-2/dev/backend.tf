terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-915518282381.s3-bucket"
    key            = "us-west-2/dev"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-dev-us-west-2-tfstate-sandbox-915518282381.dynamodb-table"
  }
}
