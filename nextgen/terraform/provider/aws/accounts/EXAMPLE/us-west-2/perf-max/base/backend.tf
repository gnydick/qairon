terraform {
  backend "s3" {
    bucket         = "terraform-state-backend-407733091588"
    key            = "${var.region}/${var.evironment}"
    region         = "${var.region}"
    dynamodb_table = "terraform-lock-state"
  }
}
