variable "environment" {}
variable "config_name" {}
variable "region" {}


variable "vpc_cidr" {}
variable "azs" {
  type = list
}

variable "extra_tags" {
  type = map
}

variable "vpc_number" {}
variable "vpc_add_cidrs" {
  type = map
}
variable "public_subnet_cidrs" {
  type=list
}

variable "private_subnet_cidrs" {
  type=list
}