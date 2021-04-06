variable "environment" {default="prod"}
variable "config_name" {}
variable "region" {}


variable "vpc_cidr" {}

variable "azs" {
  type = "list"
}

variable "private_subnet_cidrs" {
  type = "list"
}


variable "public_subnet_cidrs" {
  type = "list"
}

variable "cluster_number" {
  default = {"ng-prod1" = "1"}
  type = "map"

}
variable "deployment_target" {
  default = "ng-prod1-us-west-2-eks"
}
variable "vpc_id" {}

variable "key_name" {
  default = "ng-prod1"
}


variable "nodegroup_number" {
  default = 1
}
variable "extra_tags" {
  type = "map"
}

variable "cp_sg_id" {}
variable "private_subnet_ids" {
  type = "list"
}
variable "public_subnet_ids" {
  type = "list"
}


variable "nodegroup_count" { default = 2 }
variable "root_ebs_size" { default = 10 }
variable "node_volume_size" { default = 1024 }
variable "infra_nodegroup_ami" { default = "ami-086d9c07b8773c87d" }
variable "infra_max_size" { default = 8 }
variable "infra_scaling_desired_capacity" { default = 6 }
variable "infra_min_size" { default = 1 }
variable "infra_bootstrap_arguments" { default = "--kubelet-extra-args --node-labels=role=infra,jenkins=true --enable-docker-bridge true --client-ca-file=$CA_CERTIFICATE_FILE_PATH" }
variable "infra_instance_type" { default = "m5.large" }
variable "foo_nodegroup_ami" { default = "ami-086d9c07b8773c87d" }
variable "foo_max_size" { default = 12 }
variable "foo_scaling_desired_capacity" { default = 6 }
variable "foo_min_size" { default = 1 }
variable "foo_bootstrap_arguments" { default = "--kubelet-extra-args --node-labels=role=foo  --client-ca-file=$CA_CERTIFICATE_FILE_PATH" }
variable "foo_instance_type" { default = "m5.4xlarge" }
variable "eks_version" { default = 1.12}
