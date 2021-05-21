variable "public_subnet_cidrs" {
  type = "list"
}

variable "private_subnet_cidrs" {
  type = "list"
}


variable "region" {}
variable "config_name" {}
variable "azs" {
  type = "list"
}
variable "environment" {}
variable "vpc_id" {}



variable "extra_tags" {
  type = "map"
}

variable "kube_extra_tags" {
  type = "map"
}


variable "global_maps" {
  type = map(map(string))
}
variable "global_strings" {}

