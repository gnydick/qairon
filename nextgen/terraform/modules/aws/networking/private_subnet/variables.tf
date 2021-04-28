variable "vpc_id" {
  description = "The VPC Id"
  type        = string
  default     = ""
}

variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type        = list(string)
  default     = []
}

variable "private_subnets" {
  description = "A list of private subnets inside the VPC"
  type        = list(string)
  default     = []
}

variable "private_subnet_suffix" {
  description = "Suffix to append to private subnets name"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Name to be used on all the resources as identifier"
  type        = string
  default     = ""
}

variable "private_subnet_tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}

variable "tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}