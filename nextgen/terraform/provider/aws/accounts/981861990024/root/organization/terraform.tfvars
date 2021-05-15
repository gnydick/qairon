org = "withme"
dept = "services"
environment = "infra"
role = "it"
config = "default"
region = "us-west-2"


accounts = {
  "aws_management_sandbox" = {
    "name" = "aws-management-sandbox"
    "email" = "aws-management-sandbox@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "audit" = {
    "name" = "Audit"
    "email" = "audit-aws-981861990024@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "log_archive" = {
    "name" = "Log Archive"
    "email" = "log-archive-aws-981861990024@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "terraform_sandbox" = {
    "name" = "TerraformSandbox"
    "email" = "aws-981861990024-tf-sandbox@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "log_archive" = {
    "name" = "Log Archive"
    "email" = "log-archive-aws-981861990024@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_jgelin_sandbox" = {
    "name" = "ImvuJgelinSandbox"
    "email" = "aws-981861990024-imvu-jgelin-sandbox@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
}
