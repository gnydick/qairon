variable "region" {
}

variable "accepter-account" {
  type = map(string)
}

variable "accepter-vpc_id" {
  type = map(string)
}

variable "accepter-cidr" {
  type = map(string)
}

variable "requester_cidr" {
}

variable "requester_vpc" {
}

variable "requester_vpc_id" {
}

variable "environment" {
}

variable "config_name" {
}

variable "accepter-sgs" {
  type = map(string)
}

variable "allow_dns_out" {
}

variable "status" {
  type = map(string)
}

variable "requester_sgs_tag_name" {
}

