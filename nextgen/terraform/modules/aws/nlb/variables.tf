variable "environment" {
}

variable "region" {
}

variable "vpc_id" {
}

variable "name" {
}

variable "internal" {
}

variable "security_groups" {
  type = list(string)
}

variable "subnets" {
  type = list(string)
}

variable "deletion_protection" {
}

variable "extra_tags" {
  type = map(string)
}

variable "deployment_target" {
}

variable "config_name" {
}

variable "tier" {
}

variable "cross_zone" {
}

