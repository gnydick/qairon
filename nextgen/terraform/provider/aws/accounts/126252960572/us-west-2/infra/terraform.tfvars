org = "withme"
dept = "services"
environment = "infra"
role = "automation"
config = "default"
region = "us-west-2"
provider_region = "us-west-2"





public_subnets = {
  "vpc1": [
      "10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24"
    ]


}

private_subnets = {
  "vpc1": {
  "eks":  [     "10.0.5.0/24", "10.0.6.0/24", "10.0.7.0/24", "10.0.8.0/24"   ],
    "rds" = ["10.0.9.0/24", "10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
  }
}

eks_configs = {
  "vpc1" = {
    "infra1" = {
      azs = [],
      cluster_create_timeout = "90m",
      cluster_delete_timeout = "90m",
      cluster_egress_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24", "10.0.7.0/24", "10.0.8.0/24"],
      cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"],
      cluster_endpoint_private_access = true,
      cluster_endpoint_public_access = true,
      cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"],
      cluster_log_retention_in_days = 90,
      cluster_name = "infra1",
      eks_version = "1.20"
    }
  }
}

azs = ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"]



vpc_configs = {
  "vpc1" = {

    name = "vpc1"
    enable_dns_support = true,
    enable_dns_hostnames = true,
    cidr = "10.0.0.0/16"
  }
}




nodegroup_configs = {
  "vpc1" = {
    "infra1" = {
      "nodegroup1" = {
        name = "nodegroup1"
        bootstrap_arguments = "",
        key_name = "infra1",
        ami = "ami-0010b93bf152621e5",
        subnets = [],
        node_group_name = "nodegroup1",
        min_size = 1,
        max_size = 16,
        node_instance_type = "m5.large",
        node_volume_size = 1000,
        node_auto_scaling_group_desired_capacity = 8,
        associate_public_ip_address = false,
      }
    }
  }
}

