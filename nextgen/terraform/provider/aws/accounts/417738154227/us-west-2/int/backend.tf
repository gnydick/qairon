terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-417738154227.s3-bucket"
    key            = "us-west-2/int"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-int-us-west-2-tfstate-default-417738154227.dynamodb-table"
  }
}
