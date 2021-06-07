org             = "withme"
dept            = "engineering"
environment     = "prod"
role            = "automation"
config          = "sandbox"
region          = "us-west-2"
provider_region = "us-west-2"


public_subnets = {
  "vpc0" = {
    "eks_nodes" = [],
    "nat_gw" = ["10.101.0.64/28", "10.101.0.80/28", "10.101.0.96/28", "10.101.0.112/28"]
  }
}

private_subnets = {
  "vpc0" = {
    "eks_nodes" = ["10.101.4.0/24", "10.101.5.0/24", "10.101.6.0/24", "10.101.7.0/24"],
    "eks_cp" = ["10.101.0.0/28", "10.101.0.16/28", "10.101.0.32/28", "10.101.0.48/28"],
    "rds" = [ "10.101.8.64/26", "10.101.8.128/26", "10.101.8.192/26", "10.101.9.0/26"],
    "windows_asg" = ["10.101.0.128/28", "10.101.0.144/28", "10.101.0.160/28", "10.101.0.176/28"]
  }
}

eks_configs = {
  "vpc0" = {
    "prod0" = {
      azs                                  = [],
      cluster_create_timeout               = "90m",
      cluster_delete_timeout               = "90m",
      cluster_egress_cidrs                 = ["0.0.0.0/0"],
      cluster_enabled_log_types            = ["api", "audit", "authenticator", "controllerManager", "scheduler"],
      cluster_endpoint_private_access      = true,
      cluster_endpoint_public_access       = true,
      cluster_endpoint_public_access_cidrs = ["0.0.0.0/0"],
      cluster_log_retention_in_days        = 90,
      cluster_name                         = "prod0",
      eks_version                          = "1.20"
    }
  }
}

azs = ["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"]
vpc_configs = {
  "vpc0" = {

    name                 = "vpc0"
    enable_dns_support   = true,
    enable_dns_hostnames = true,
    cidr                 = "10.101.0.0/16"
  }
}

nodegroup_configs = {
  "vpc0" = {
    "prod0" = {
      "nodegroup0" = {
        name                                     = "nodegroup0"
        bootstrap_arguments                      = "",
        key_name                                 = "prod-vpc0-prod0",
        ami                                      = "ami-0010b93bf152621e5",
        subnets                                  = [],
        node_group_name                          = "nodegroup0",
        min_size                                 = 1,
        max_size                                 = 16,
        node_instance_type                       = "m5.large",
        node_volume_size                         = 1000,
        node_auto_scaling_group_desired_capacity = 8,
        associate_public_ip_address              = false,
      }
    }
  }
}

