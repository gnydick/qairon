org = "withme"
dept = "services"
environment = "infra"
role = "it"
config = "default"
region = "us-west-2"
provider_region = "us-west-2"

account_tags = {
  "aws_management_sandbox" = {},
  "audit" = {},
  "log_archive" = {},
  "terraform_sandbox" = {},
  "log_archive" = {},
  "imvu_jgelin_sandbox" = {
    "Org" = "imvu",
    "Dept" = "rnd"
  },
}

top_level_ous = {
  "sandbox": "Sandbox",
  "security": "Security"
}

sub_ous = {
  "imvu" = {
    "name" = "Imvu",
    "parent" = "sandbox"
  },
  "jgelin" = {
    "name" = "Jgelin",
    "parent" = "imvu"
  }


}

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
  "imvu_jgelin_sandbox" = {
    "name" = "ImvuJgelinSandbox"
    "email" = "aws-981861990024-imvu-jgelin-sandbox@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
}
