variable "region" {
}

variable "environment" {
}

variable "config_name" {
}

variable "fqdn" {
}

variable "extra_tags" {
  type    = map(string)
  default = {}
}

variable "deployment_target" {
}

variable "vpc_id" {
}
