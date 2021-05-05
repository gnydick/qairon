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

variable "deployment_target" {
}

variable "public_subnet_cidrs" {
  type = list(string)
}

variable "ami" {
}

variable "key_name" {
}

variable "cluster_number" {
}

variable "vpc_id" {
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "cluster_name" {
}

