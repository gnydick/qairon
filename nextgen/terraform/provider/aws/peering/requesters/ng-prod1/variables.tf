variable "region" {}
variable "accepter-account" {type="map"}
variable "accepter-vpc_id" {type="map"}
variable "accepter-cidr" {type="map"}
variable "requester_cidr" {}
variable "requester_vpc" {}
variable "requester_vpc_id" {}
variable "environment" {}

variable "config_name" {}
variable "accepter-sgs" {type="map"}
variable "allow_dns_out" {}

variable "status" { type="map" }
variable "requester_sgs_tag_name" {}