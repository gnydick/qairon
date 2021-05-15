terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.40.0"
    }
  }
}


provider "aws" {
  region=var.region
  default_tags {
    tags = var.global_maps.global_tags
  }
}