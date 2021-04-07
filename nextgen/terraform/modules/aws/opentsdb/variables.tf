variable "environment" {
}

variable "config_name" {
}

variable "region" {
}

variable "vpc_cidr" {
}

variable "azs" {
  type = list(string)
}

variable "private_subnet_cidrs" {
  type = list(string)
}

variable "vpc_id" {
}

variable "public_subnet_cidrs" {
  type = list(string)
}

variable "subnet_id" {
}

variable "key_name" {
}

variable "account_no" {
}

variable "emr_version" {
}

variable "core_instance_type" {
}

variable "master_instance_type" {
}

variable "emr_core_count" {
}

variable "root_ebs_size" {
}

variable "ebs_core_size" {
}

variable "ebs_core_type" {
}

variable "volumes_per_core_instance" {
}

variable "volumes_per_master_instance" {
}

variable "ebs_master_size" {
}

variable "ebs_master_type" {
}

variable "termination_protection" {
}

