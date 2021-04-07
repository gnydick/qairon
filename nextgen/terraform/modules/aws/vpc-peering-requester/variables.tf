variable "region" {
}

variable "accepter_account" {
}

variable "accepter_vpc_id" {
}

variable "accepter_cidr" {
}

variable "requester_cidr" {
}

variable "requester_private_route_table_ids" {
  type = list(string)
}

variable "requester_vpc" {
}

variable "requester_vpc_id" {
}

variable "allow_dns_out" {
}

