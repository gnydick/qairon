variable "cluster" {}

variable "config_name" {
  default = "openvpn"
}

variable "vpc_id" {}
variable "vpc_cidr" {}
variable "public_subnet_ids" {}
variable "ssl_cert" {}
variable "ssl_key" {}

variable "private_key" {}

variable "ami" {}
variable "instance_type" {}
variable "bastion_host" {}
variable "bastion_user" {}
variable "openvpn_user" {}
variable "openvpn_admin_user" {}
variable "openvpn_admin_pw" {}
variable "vpn_cidr" {}
variable "sub_domain" {}
variable "route_zone_id" {}

variable "deployment_target" {}