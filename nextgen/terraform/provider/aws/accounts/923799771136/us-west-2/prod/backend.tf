terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-923799771136.s3-bucket"
    key            = "us-west-2/prod"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-prod-us-west-2-tfstate-default-923799771136.dynamodb-table"
  }
}
