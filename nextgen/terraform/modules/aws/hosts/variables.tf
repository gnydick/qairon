variable "aws_region" {
}

variable "host_count" {
}

variable "security_groups" {
  type = list(string)
}

variable "zone_id" {
}

variable "instance_type" {
}

variable "amis" {
  type = list(string)
}

variable "azs" {
  type = list(string)
}

variable "associate_public_ip_address" {
}

variable "key_name" {
}

variable "subnet_ids" {
  type = list(string)
}

variable "role" {
}

variable "host_docker_vol_count" {
}

variable "docker_image_vol_size" {
}

variable "docker_image_device_name" {
}

variable "rancher_service_template" {
}

variable "iam_instance_profile" {
}

variable "delete_docker_ebs_on_termination" {
}

variable "token" {
}

variable "checksum" {
}

variable "kube_role" {
}

variable "destroy_command" {
}

variable "rancher_url" {
}

variable "custom_tags" {
  type = map(string)
}

variable "deployment_target" {
}

variable "environment" {
}

variable "config_name" {
}

variable "region" {
}

variable "vpc_id" {
}

