variable "config_name" {
}

variable "environment" {
}

variable "accepter-sgs" {
  type = list(string)
}

variable "requester_sgs" {
  type = list(string)
}

variable "status" {
}

variable "requester_eks_sgs" {
  type = list(string)
}

