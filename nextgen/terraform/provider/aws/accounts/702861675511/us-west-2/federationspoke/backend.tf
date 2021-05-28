terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-702861675511.s3-bucket"
    key            = "us-west-2/federationspoke"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-dev-us-west-2-tfstate-default-702861675511.dynamodb-table"
  }
}
