terraform {


  backend "s3" {
    bucket = "terraform-state-backend-407733091588"
    key = "route53/hosted_zones"
    region = "us-west-2"
    dynamodb_table = "terraform-lock-state"


  }

}
