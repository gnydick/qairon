variable "azs" {
  type = list
}
variable "config_name" {}

variable "environment" {}


variable "vpc_add_cidr" {
  type= map
}

variable "private_subnet_cidrs" {
  type = list(string)
}
variable "public_subnet_cidrs" {
  type = list(string)
}
variable "region" {}


variable "vpc_cidr" {}




variable "backend_bucket" {}
variable "statefile_name" {}
variable "locking_dsn" {}