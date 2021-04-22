variable "environment" {
  description = "Name of current environment"
  type        = string
  default     = "perf-max"
}

variable "region" {
  description = "Name of current region"
  type        = string
  default     = "us-west-2"
}

variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type        = list(string)
  default     = [us-west-2a, us-west-2b, us-west-2c]
}


# variable "azs" {
#   type = list
# }
# variable "config_name" {}
#
# variable "environment" {
#   type = string
#   default = "perf-max"
# }
#
#
# variable "vpc_add_cidr" {
#   type= map
# }
#
# variable "private_subnet_cidrs" {
#   type = list(string)
# }
# variable "public_subnet_cidrs" {
#   type = list(string)
# }
# variable "region" {
#   type = string
#   default = "us-west-2"
# }
#
#
# variable "vpc_cidr" {}
#
#
#
#
# variable "backend_bucket" {}
# variable "statefile_name" {}
# variable "locking_dsn" {}
