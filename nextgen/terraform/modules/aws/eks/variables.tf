variable "vpc_id" {}
variable "private_subnets_ids" {
  type = list(string)
}

variable "eks_config" {
  type = object({
    cluster_name                         = string,
    cluster_enabled_log_types            = list(string),
    eks_version                          = string,
    cluster_endpoint_private_access      = bool,
    cluster_endpoint_public_access       = bool,
    cluster_endpoint_public_access_cidrs = list(string),
    cluster_create_timeout               = string,
    cluster_delete_timeout               = string,
    cluster_log_retention_in_days        = number,
    cluster_egress_cidrs                 = list(string)
  })
}


variable "global_maps" {
  type = map(map(string))
}
variable "global_strings" {}