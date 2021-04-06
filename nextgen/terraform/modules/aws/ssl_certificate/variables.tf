variable "region" {}
variable "environment" {}
variable "fqdn" {}
variable "config_name" {}
variable "validation_emails" {
  type = "list"
}
variable "extra_tags" {
  type = "map"
}
