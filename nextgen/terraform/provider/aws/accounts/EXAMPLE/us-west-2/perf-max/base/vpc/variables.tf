variable "vpc_cidr" {
  description = "The CIDR block for the VPC. Default value is a valid CIDR, but not acceptable by AWS and should be overridden"
  type        = string
}

variable "environment" {
  description = "Name of current environment"
  type        = string
  default     = ""
}

variable "region" {
  description = "Name of current region"
  type        = string
  default     = ""
}
