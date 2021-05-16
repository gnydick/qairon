variable "accounts" {
  type = map(map(string))
}

variable "account_tags" {
  type = map(map(string))
}

variable "top_level_ous" {
  type = map(string)
}
//
//variable "sub_ous" {
//  type = map(map(string))
//}