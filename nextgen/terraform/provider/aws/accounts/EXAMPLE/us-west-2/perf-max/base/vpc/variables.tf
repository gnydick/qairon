variable "vpc_cidr" {
  description = "The CIDR block for the VPC. Default value is a valid CIDR, but not acceptable by AWS and should be overridden"
  type        = string
  default     = "20.10.0.0/16"
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

variable "azs" {
  description = "A list of availability zones names or ids in the region"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "map_public_ip_on_launch" {
  description = "Should be false if you do not want to auto-assign public IP on launch"
  type        = bool
  default     = true
}

variable "public_subnets_cidr" {
  description = "A list of public subnets CIDR"
  type        = list(string)
  default     = ["20.10.11.0/24", "20.10.12.0/24", "20.10.13.0/24"]
}

variable "private_subnets_cidr" {
  description = "A list of private subnets CIDR"
  type        = list(string)
  default     = ["20.10.1.0/24", "20.10.2.0/24", "20.10.3.0/24"]
}

variable "public_subnet_suffix" {
  description = "Suffix to append to public subnets name"
  type        = string
  default     = "public"
}

variable "private_subnet_suffix" {
  description = "Suffix to append to private subnets name"
  type        = string
  default     = "private"
}

variable "public_subnet_tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {
    "kubernetes.io/cluster/perf-1-us-west-2-eks" = "shared"
    "kubernetes.io/role/elb" = ""
  }
}

variable "private_subnet_tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {
    "kubernetes.io/cluster/perf-1-us-west-2-eks" = "shared"
    "kubernetes.io/role/internal-elb" = ""
  }
}

variable "tags" {
  description = "A map of tags to add to subnets"
  type        = map(string)
  default     = {}
}