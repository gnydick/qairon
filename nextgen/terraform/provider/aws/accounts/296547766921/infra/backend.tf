terraform {
  backend "s3" {
    bucket = "terraform-state-backend-296547766921.s3-bucket"
    key = "us-west-2/infra"
    region = "us-west-2"
    dynamodb_table = "withme-services-sandbox-us-west-2-tfstate-default-296547766921.dynamodb-table"
  }
}
