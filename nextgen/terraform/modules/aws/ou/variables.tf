variable "name" {}
variable "parent" {}
variable "tags" {
  type = map(string)
  default = {}
}