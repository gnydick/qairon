environment = "perf"
config = "default"
org = "withme"
region = "us-west-2"
dept = "services"


map_public_ip = {
  "perf-1": false
}

vpc_cidr = {
  "vpc-1": "20.10.0.0/16"
}


public_subnets = {
  "vpc-1": {
    "perf-1": [
      "20.10.11.0/24", "20.10.12.0/24", "20.10.13.0/24"
    ]
  }
}

private_subnets = {
  "vpc-1": {
    "perf-1": [
      "20.10.1.0/24", "20.10.2.0/24", "20.10.3.0/24"
    ]
  }
}


azs = ["us-west-2a", "us-west-2b", "us-west-2c"]

eks_versions = {
  "vpc-1": {
    "perf-1": 1.19
  }
}
//
//
//
//
//variable "public_subnet_tags" {
//  description = "A map of tags to add to subnets"
//  type        = map(string)
//  default     = {
//    "kubernetes.io/cluster/perf-1-us-west-2-eks" = "shared"
//    "kubernetes.io/role/elb" = ""
//  }
//}
//
//variable "private_subnet_tags" {
//  description = "A map of tags to add to subnets"
//  type        = map(string)
//  default     = {
//    "kubernetes.io/cluster/perf-1-us-west-2-eks" = "shared"
//    "kubernetes.io/role/internal-elb" = ""
//  }
//}
//
//variable "tags" {
//  description = "A map of tags to add to subnets"
//  type        = map(string)
//  default     = {}
//}