variable "vpc_id" {}
variable "environment" {}
variable "region" {}
variable "config_name" {}
variable "deployment_target" {}
variable "extra_tags" { type = "map" }
variable "cluster_number" {}
variable "proxy_sg_name_override" {
  default = ""
}