variable "environment" {
  default = "perf-1"
}

#variable "config_name" {
#}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "cluster_number" {
  default = {
    "perf-1" = "1"
  }
  type = map(string)
}

#variable "deployment_target" {
#  default = "perf-1-us-west-2-eks"
#}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
  default     = ""
}

variable "cluster_endpoint_public_access" {
  description = "Indicates whether or not the Amazon EKS public API server endpoint is enabled."
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "List of CIDR blocks which can access the Amazon EKS public API server endpoint."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "cluster_egress_cidrs" {
  description = "List of CIDR blocks that are permitted for cluster egress traffic."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "cluster_log_retention_in_days" {
  default     = 90
  description = "Number of days to retain log events. Default retention - 90 days."
  type        = number
}

variable "extra_tags" {
  type = map(string)
}

variable "public_subnets_ids" {
  description = "ID's of the Public subnets in the VPC"
  type = list(string)
}

variable "private_subnets_ids" {
  description = "ID's of the Private subnets in the VPC"
  type = list(string)
}

variable "eks_version" {
  description = "Kubernetes version to use for the EKS cluster."
  type        = string
}

variable "cluster_iam_role_name" {
  description = "IAM role name for the cluster."
  type        = string
  default     = ""
}