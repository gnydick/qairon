variable "name" {
  description = "(Required) Name of the repository"
  type        = string
}

variable "scan_on_push" {
  type = bool
}