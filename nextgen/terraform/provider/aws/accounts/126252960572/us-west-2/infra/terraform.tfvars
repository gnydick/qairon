org = "withme"
dept = "services"
environment = "infra"
role = "automation"
config = "default"
region = "us-west-2"
provider_region = "us-west-2"

map_public_ip_on_launch = {
  "vpc1": {
    "infra1": false
  }
}

vpc_cidrs = {
  "vpc1": "10.0.0.0/16"
}

cluster_endpoint_public_access = {
  "vpc1": {
    "infra1": true
  }
}

public_subnets = {
  "vpc1": {
    "infra1": [
      "10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24"
    ]
  }
}

private_subnets = {
  "vpc1": {
    "infra1": [
      "10.0.5.0/24", "10.0.6.0/24", "10.0.7.0/24", "10.0.8.0/24"
    ]
  }
}


azs = ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"]

eks_versions = {
  "vpc1": {
    "infra1": "1.19"
  }
}

cluster_enabled_log_types = {
  "vpc1": {
    "infra1": []
  }
}

structure = {
  "vpc1": ["infra1"]
}