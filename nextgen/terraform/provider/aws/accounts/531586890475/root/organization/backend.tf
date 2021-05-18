terraform {
  backend "s3" {
    bucket = "terraform-state-backend-531586890475.s3-bucket"
    key = "root/organization"
    region = "us-west-2"
    dynamodb_table = "togetherlabs-it-infra-us-west-2-tfstate-default-531586890475.dynamodb-table"
  }
}
