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

variable "public_subnets_cidr" {
  description = "A list of public subnets CIDR"
  type        = list(string)
  default     = []
}

variable "private_subnets_cidr" {
  description = "A list of private subnets CIDR"
  type        = list(string)
  default     = []
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

variable "private_subnets_tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}

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
# variable "backend_bucket" {}
# variable "statefile_name" {}
# variable "locking_dsn" {}
