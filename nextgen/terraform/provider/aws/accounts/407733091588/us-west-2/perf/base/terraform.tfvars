environment = "perf"
config = "default"
org = "withme"
region = "us-west-2"
dept = "services"
role = "dev"

map_public_ip = {
  "perf-1": false
}

vpc_cidrs = {
  "vpc-1": "20.10.0.0/16"
}

cluster_endpoint_public_access = {
  "vpc-1": {
    "perf-1": true
  }
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

cluster_enabled_log_types = {
  "vpc-1": {
    "perf-1": []
  }
}

structure = {
  "vpc-1": ["perf-1"]
}