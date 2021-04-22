variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type        = list(string)
  default     = []
}
variable "private_subnets_cidr" {
  description = "A list of private subnets CIDR"
  type        = list(string)
  default     = []
}
variable "private_subnet_suffix" {
  description = "Suffix to append to private subnets name"
  type        = string
  default     = "private"
}
variable "vpc_id" {
  description = "The VPC Id"
  type        = string
  default     = ""
}
variable "name" {
  description = "Name to be used on all the resources as identifier"
  type        = string
  default     = ""
}
variable "tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}
variable "private_subnets_tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}