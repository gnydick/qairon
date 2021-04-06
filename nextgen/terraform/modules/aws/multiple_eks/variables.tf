variable "environment" {}
variable "config_name" {}
variable "region" {}


variable "vpc_cidr" {}

variable "azs" {
  type = "list"
}

variable "private_subnet_cidrs" {
  type = "list"
}


variable "deployment_target" {}


variable "public_subnet_cidrs" {
  type = "list"
}

variable "ami" {}

variable "key_name" {}
variable "cluster_number" {}
variable "vpc_id" {}
variable "public_subnet_ids" {
  type = "list"
}
variable "private_subnet_ids" {
  type = "list"
}
variable "cluster_name" {}
