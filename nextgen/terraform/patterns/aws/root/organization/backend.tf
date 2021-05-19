terraform {
  backend "s3" {
    bucket = "terraform-state-backend-<ACCOUNT_ID>.s3-bucket"
    key = "root/organization"
    region = "<REGION>"
    dynamodb_table = "<ORG>.<DEPT>.<ENV>.<REGION>.tfstate.default-<ACCOUNT_ID>.dynamodb-table"
  }
}
