variable "map_public_ip_on_launch" {
  type = map(map(bool))
  description = "whether or not to map a public IP to the nodes in a target (cluster)"
}
variable "public_subnets" {
  type = map(map(list(string)))
}

variable "private_subnets" {
  type = map(map(list(string)))
}

variable "vpc_cidrs" {
  type = map
}


variable "azs" {
  type = list
}

variable "eks_versions" {
  type = map
}


variable "cluster_endpoint_public_access" {
  type = map(map(bool))
}

variable "cluster_enabled_log_types" {
  type = map(map(list(string)))
}

variable "structure" {
  type = map(list(string))
}