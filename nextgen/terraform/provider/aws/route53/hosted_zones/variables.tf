variable "region" {}

variable "environment" {}
variable "config" {}
variable "zones" {
  type = map(map(string))
}

variable "tier" {}
variable "role" {}
variable "dept" {
}
variable "org"{}
variable "subdomains" {
  type = map(map(map(string)))
}