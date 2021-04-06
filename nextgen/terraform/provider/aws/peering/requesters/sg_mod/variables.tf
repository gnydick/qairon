variable "config_name" {}
variable "environment" {}
variable "accepter-sgs" {type="list"}

variable "requester_sgs" {type="list"}
variable "status" {}
variable "requester_eks_sgs" {
  type = "list"
}