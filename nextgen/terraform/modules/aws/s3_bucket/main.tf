variable "region" {
  default = ""
}

variable "s3_acl" {
  default = ""
}

variable "bucket" {
  default = ""
}

variable "role" {
  default = ""
}

variable "environment" {
  default = ""
}

variable "config_name" {
  default = ""
}

resource "aws_s3_bucket" "rancher-server-access-logs" {
  bucket = var.bucket
  region = var.region
  acl    = var.s3_acl

  tags = {
    Region                                  = var.region
    Environment                             = var.environment
    Name                                    = "${var.environment}.${var.region}.rancher-server-access-logs.s3_bucket"
    Config                                  = var.config_name
    GeneratedBy                             = "terraform"
    "kubernetes.io/cluster/prod1-us-west-2" = "owned"
  }
}

