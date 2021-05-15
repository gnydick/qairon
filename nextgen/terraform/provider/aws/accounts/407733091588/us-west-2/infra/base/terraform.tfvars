environment = "infra"
config = "default"
org = "withme"
region = "us-west-2"
dept = "services"
role = "automation"

# structure = { vpc: [ deployment_targets ] }
structure = {
  "vpc1": [ "eks1" ]
}


map_public_ip_on_launch = {
  "vpc1": {
    "eks1": false
  }
}

vpc_cidrs = {
  "vpc1": "10.0.0.0/16"
}

cluster_endpoint_public_access = {
  "vpc1": {
    "eks1": true
  }
}

public_subnets = {
  "vpc1": {
    "eks1": [
      "10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"
    ]
  }
}

private_subnets = {
  "vpc1": {
    "eks1": [
      "10.0.3.0/24", "10.0.4.0/24", "10.0.5.0/24"
    ]
  }
}


azs = ["us-west-2a", "us-west-2b", "us-west-2c"]

eks_versions = {
  "vpc1": {
    "eks1": "1.19"
  }
}

cluster_enabled_log_types = {
  "vpc1": {
    "eks1": []
  }
}

