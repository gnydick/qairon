terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-132868707156.s3-bucket"
    key            = "us-west-2/federationspoke"
    region         = "us-west-2"
    dynamodb_table = "withme-engineering-perf-us-west-2-tfstate-default-132868707156.dynamodb-table"
  }
}
