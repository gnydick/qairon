variable "environment" {
  description = "Name of current environment"
  type        = string
  default     = "perf-1"
}

variable "region" {
  description = "Name of current region"
  type        = string
  default     = "us-west-2"
}

variable "tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}
