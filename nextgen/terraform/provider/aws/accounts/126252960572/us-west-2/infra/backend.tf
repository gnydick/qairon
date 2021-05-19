terraform {
  backend "s3" {
    bucket = "terraform-state-backend-126252960572.s3-bucket"
    key = "us-west-2/infra"
    region = "us-west-2"
    dynamodb_table = "withme-engineering-infra-us-west-2-tfstate-default-126252960572.dynamodb-table"
  }
}
