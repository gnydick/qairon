variable "vpc_id" {}
variable "eks_config" {
  type = object({
    cluster_name = string,
    cluster_enabled_log_types = list(string),
    eks_version = string,
    cluster_endpoint_private_access = bool,
    cluster_endpoint_public_access = bool,
    cluster_endpoint_public_access_cidrs = list(string),
    cluster_create_timeout = string,
    cluster_delete_timeout = string,
    cluster_log_retention_in_days = number,
    cluster_egress_cidrs = list(string)
  })
}

variable "nodegroup_configs" {
  type = map(object({
    bootstrap_arguments = string,
    key_name = string,
    ami = string,
    name = string,
    min_size = number,
    max_size = number,
    node_instance_type = string,
    node_volume_size = number,
    node_auto_scaling_group_desired_capacity = number,
    associate_public_ip_address = bool
  }))
}


variable "azs" {
  type = list(string)
}

variable "public_subnets" {
  type = list(string)
}
variable "private_subnets" {
  type = list(string)
}

variable "global_maps" {
  type = map(map(string))
}
variable "global_strings" {}