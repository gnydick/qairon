variable "cluster_name" {}
variable "name" {}
variable "config_name" {}
variable "deployment_target" {}
variable "environment" {}
variable "extra_tags" { type = "map" }
variable "lb_sgs" {type = "list"}
variable "ingress_subnet_ids" { type = "list" }
variable "region" {}
variable "role" {}
variable "healthcheck_target" {}
variable "healthcheck_healthy_threshold" {}
variable "healthcheck_unhealthy_threshold" {}
variable "healthcheck_interval" {}
variable "healthcheck_timeout" {}
variable "listener_instance_port" {}
variable "listener_instance_protocol" {}
variable "listener_lb_port" {}
variable "listener_lb_protocol" {}