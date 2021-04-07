variable "public_subnet_cidrs" {
  type = list(string)
}

variable "private_subnet_cidrs" {
  type = list(string)
}

variable "region" {
}

variable "config_name" {
}

variable "azs" {
  type = list(string)
}

variable "environment" {
}

variable "vpc_id" {
}

variable "extra_tags" {
  type = map(string)
}

variable "kube_extra_tags" {
  type = map(string)
}

