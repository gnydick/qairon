terraform {
  backend "s3" {
    bucket = "terraform-state-backend-981861990024.s3-bucket"
    key = "root/organization"
    region = "us-west-2"
    dynamodb_table = "withme-services-sandbox-us-west-2-tfstate-default-981861990024.dynamodb-table"
  }
}
