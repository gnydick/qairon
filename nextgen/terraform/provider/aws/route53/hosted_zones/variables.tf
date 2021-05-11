variable "region" {}

variable "environment" {}
variable "config" {}
variable "zones" {
  type = list(string)
}

variable "tier" {}
variable "role" {}
variable "dept" {
}
variable "org"{}
variable "subdomains" {
  type = map(list(string))
}