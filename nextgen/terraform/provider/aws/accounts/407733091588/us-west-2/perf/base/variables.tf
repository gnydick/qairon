variable "environment" {
  description = "Name of current environment"
  type        = string
}

variable "region" {
  description = "Name of current region"
  type        = string
}

variable "map_public_ip" {
  type = map
  description = "whether or not to map a public IP to the nodes in a target (cluster)"
}
variable "config" {
  type = string
}

variable "public_subnets" {
  type = map
}

variable "private_subnets" {
  type = map
}

variable "vpc_cidr" {
  type = map
}


variable "azs" {
  type = list
}

variable "eks_versions" {
  type = map
}

variable "role" {
  type = string
}