variable "environment" {
  description = "Name of current environment"
  type = string
}
variable "config" {
  type = string
}

variable "region" {
  description = "AWS region"
  type = string
}

variable "vpc_id" {
  description = "ID of the VPC"
  type = string
  default = ""
}

variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type = list(string)
  default = []
}

variable "name_prefix" {
  description = "Name of the EKS cluster. Also used as a prefix in names of related resources."
  type = string
}

variable "name" {
  type = string
}

variable "cluster_number" {
  type = string
}

#variable "deployment_target" {
#}

variable "eks_version" {
  description = "Kubernetes version to use for the EKS cluster."
  type = string
}

variable "cluster_endpoint_public_access" {
  description = "Indicates whether or not the Amazon EKS public API server endpoint is enabled."
  type = bool
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "List of CIDR blocks which can access the Amazon EKS public API server endpoint."
  type = list(string)
}

variable "public_subnets_ids" {
  description = "ID's of the Public subnets in the VPC"
  type = list(string)
}

variable "private_subnets_ids" {
  description = "ID's of the Private subnets in the VPC"
  type = list(string)
}

variable "cluster_egress_cidrs" {
  description = "List of CIDR blocks that are permitted for cluster egress traffic."
  type = list(string)
}

variable "cluster_endpoint_private_access" {
  description = "Indicates whether or not the Amazon EKS private API server endpoint is enabled."
  type = bool
}

variable "tags" {
  description = "A map of tags to add to all resources. Tags added to launch configuration or templates override  these values for ASG Tags only."
  type = map(string)
}

variable "cluster_enabled_log_types" {
  description = "A list of the desired control plane logging to enable. For more information, see Amazon EKS Control  Plane Logging documentation (https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html)"
  type = list(string)
}

variable "cluster_create_timeout" {
  description = "Timeout value when creating the EKS cluster."
  type = string
  default = "35m"
}

variable "cluster_delete_timeout" {
  description = "Timeout value when deleting the EKS cluster."
  type = string
  default = "20m"
}

variable "cluster_log_retention_in_days" {
  description = "Number of days to retain log events. Default retention - 90 days."
  type = number
}
