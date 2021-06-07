terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-190120512280.s3-bucket"
    key            = "us-west-2/int"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-int-us-west-2-tfstate-sandbox-190120512280.dynamodb-table"
  }
}
