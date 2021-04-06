variable "environment" {}
variable "config_name" {}
variable "region" {}


variable "vpc_cidr" {}

variable "azs" {
  type = "list"
}


variable "cluster_name" {}

variable "deployment_target" {}

variable "eks_version" {}

variable "key_name" {}
variable "vpc_id" {}
variable "public_subnet_ids" {
  type = "list"
}
variable "private_subnet_ids" {
  type = "list"
}

