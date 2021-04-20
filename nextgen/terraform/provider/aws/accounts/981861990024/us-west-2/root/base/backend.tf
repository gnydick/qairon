
terraform {
  backend "s3" {
    bucket         = "981861990024-root"
    key            = "backend"
    region         = "us-west-2"
//    dynamodb_table = var.locking_dsn
  }
}
