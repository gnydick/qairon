variable "name" {
  description = "The name of the policy"
  type        = string
}

variable "iam_role_name" {
  description = "The name of the IAM role to which the policy should be applied"
  type        = string
}

variable "path" {
  description = "The path of the policy in IAM"
  type        = string
}

variable "description" {
  description = "The description of the policy"
  type        = string
}

variable "iam_policy_document_sid" {
  description = "Sid for IAM policy statement"
  type        = string
}

variable "iam_policy_document_effect" {
  description = "IAM policy statement effect."
  type        = string
  validation {
    condition     = var.iam_policy_document_effect == null ? true : contains(["Allow", "Deny"], var.iam_policy_document_effect)
    error_message = "IAM policy statement effect must be either `null`, \"Allow\", or \"Deny\"."
  }
}

variable "iam_policy_document_actions" {
  description = "List of policy actions that will be added to the IAM Policy"
  type        = list(string)
}

variable "iam_policy_document_resource_arn" {
  description = "AWS Resource ARN"
  type        = list(string)
}

variable "tags" {
  description = "A map of tags to add to all resources."
  type        = map(string)
}
