variable "name" {}
variable "shared_node_sg" {}
variable "nodegroup_config" {
  type = object({
    bootstrap_arguments                      = string,
    key_name                                 = string,
    ami                                      = string,
    name                                     = string,
    min_size                                 = number,
    max_size                                 = number,
    node_instance_type                       = string,
    node_volume_size                         = number,
    node_auto_scaling_group_desired_capacity = number,
    associate_public_ip_address              = bool
  })
}
variable "cp_sg_id" {}
variable "vpc_id" {}
variable "subnets" {}
variable "cluster_name" {}
variable "global_maps" {
  type = map(map(string))
}
variable "global_strings" {}