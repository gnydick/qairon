
variable "requesting-cidr" {}
variable "requesting-vpc_id" {}
variable "accepter-vpc_id" {}
variable "environment" {}
variable "deployment_target" {}
variable "config_name" {}
variable "req-sgs" {
  type = list(string)
}
variable "status" {}
variable "allow_dns_in" {}
variable "requester_account" {}