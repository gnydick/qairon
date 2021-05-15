terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-407733091588"
    key            = "us-west-2/perf-max"
    region         = "us-west-2"
    dynamodb_table = "terraform-lock-state"
  }
}
