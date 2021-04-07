variable "region" {}
variable "requesting-cidr" {
  type = "map"
}
variable "accepting-vpc_id" {}
variable "requesting-vpc_id" {
  type = "map"
}
variable "config_name" {}
variable "environment" {}
variable "deployment_target" {}
variable "req-sgs" {
  type = "map"
}
variable "sg_environment" {}
variable "status" {
  type="map"
}
variable "allow_dns_in" {
  default = ""
}
variable "requester_account" {
  type = "map"
}