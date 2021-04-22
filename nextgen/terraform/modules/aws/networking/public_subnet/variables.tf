variable "config_name" {
}

variable "vpc_id" {
}

variable "azs" {
  type = list(string)
}

variable "public_subnet_cidrs" {
  type = list(string)
}
variable "extra_tags" {
  type = map(string)
}

variable "kube_extra_tags" {
  type = map(string)
}
variable "environment" {
}

variable "region" {
}
