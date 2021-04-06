variable "region" {}
variable "accepter-account" {}
variable "accepter-vpc_id" {}
variable "accepter-cidr" {}
variable "requester_cidr" {}
variable "requester_vpc" {}
variable "requester_vpc_id" {}
variable "environment" {}

variable "config_name" {}
variable "accepter-sgs" {type="list"}
variable "allow_dns_out" {}
variable "status" {}