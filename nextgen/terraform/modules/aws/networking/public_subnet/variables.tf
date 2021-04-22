variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type        = list(string)
  default     = []
}
variable "public_subnet_suffix" {
  description = "Suffix to append to public subnets name"
  type        = string
  default     = "public"
}
variable "public_subnets_cidr" {
  description = "A list of public subnets CIDR"
  type        = list(string)
  default     = []
}
variable "vpc_id" {
  description = "The VPC Id"
  type        = string
  default     = ""
}
variable "map_public_ip_on_launch" {
  description = "Should be false if you do not want to auto-assign public IP on launch"
  type        = bool
  default     = true
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
variable "public_subnet_tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}