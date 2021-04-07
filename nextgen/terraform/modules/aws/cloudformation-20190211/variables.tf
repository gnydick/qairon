variable "key_name" {
}

variable "ami" {
}

variable "vpc_id" {
}

variable "subnets" {
}

variable "cp_sg_id" {
}

variable "min_size" {
}

variable "max_size" {
}

variable "region" {
}

variable "environment" {
}

variable "group_number" {
}

variable "config_name" {
}

variable "azs" {
}

variable "role" {
}

variable "extra_tags" {
  type = map(string)
}

variable "node_instance_type" {
}

variable "node_volume_size" {
}

variable "node_auto_scaling_group_desired_capacity" {
}

variable "associate_public_ip_address" {
  default = "false"
}

variable "bootstrap_arguments" {
  default = ""
}

variable "deployment_target" {
}

variable "cluster_name" {
}

variable "nodegroup_number" {
}

variable "proxy_security_group" {
}

