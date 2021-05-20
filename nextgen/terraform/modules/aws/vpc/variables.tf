variable "vpc_config" {
  type = object({
    name = string,
    enable_dns_support = bool,
    enable_dns_hostnames = bool,
    cidr = string
  })
}

variable "global_maps" {
  type = map(map(string))
}
variable "global_strings" {}