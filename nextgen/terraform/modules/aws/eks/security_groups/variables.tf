variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Name of current environment"
  type        = string
  default     = ""
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = ""
}

variable "config_name" {
}

variable "deployment_target" {
}

