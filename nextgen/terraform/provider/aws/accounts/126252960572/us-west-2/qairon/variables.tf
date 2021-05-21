variable "rds_subnets" {
  type = list(string)
}

variable "azs" {
  type = list(string)
}
variable "tfstate_region" {}