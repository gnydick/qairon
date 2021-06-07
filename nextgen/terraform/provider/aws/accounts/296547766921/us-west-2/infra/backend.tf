terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-296547766921.s3-bucket"
    key            = "us-west-2/infra"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-infra-us-west-2-tfstate-sandbox-296547766921.dynamodb-table"
  }
}
