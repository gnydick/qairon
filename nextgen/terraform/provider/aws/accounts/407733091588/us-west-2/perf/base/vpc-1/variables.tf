variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type = string
}

variable "environment" {
  description = "Name of current environment"
  type = string
}

variable "region" {
  description = "Name of current region"
  type = string
}

variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type = list(string)
}

variable "map_public_ip_on_launch" {
  description = "Should be false if you do not want to auto-assign public IP on launch"
  type = bool
}

variable "public_subnets" {
  description = "A list of public subnets CIDR"
  type = map
}

variable "private_subnets" {
  description = "A list of private subnets CIDR"
  type = map
}

variable "public_subnet_suffix" {
  description = "Suffix to append to public subnets name"
  type = string
}

variable "private_subnet_suffix" {
  description = "Suffix to append to private subnets name"
  type = string
}

variable "public_subnet_tags" {
  description = "A map of tags to add to subnets"
  type = map(string)
}

variable "private_subnet_tags" {
  description = "A map of tags to add to subnets"
  type = map(string)
}

variable "tags" {
  description = "A map of tags to add to subnets"
  type = map(string)
}

variable "name" {
  type = string
}



variable "number" {
}
variable "config" {
}
variable "eks_versions" {
  type = map
}