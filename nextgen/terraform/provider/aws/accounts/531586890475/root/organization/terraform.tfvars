org = "withme"
dept = "services"
environment = "infra"
role = "it"
config = "default"
region = "us-west-2"
provider_region = "us-west-2"

account_tags = {
  "it" = {},
  "audit" = {},
  "log_archive" = {},
  "log_archive" = {},
  "imvu_jgelin_sandbox" = {
    "Org" = "imvu",
    "Dept" = "rnd"
  },
  "imvu_data_analysts" = {},
  "imvu_operations" = {},
  "imvu_cs_prod" = {},
  "imvu_data_engineering" = {},
  "imvu_stayup" = {},
  "imvu_infra" = {},
  "withme_labs" = {},
  "together_labs" = {},
  "imvu_ego_services" = {},
  "imvu_ego_dev" = {},
  "imvu_data_integration" = {},
  "imvu_databricks_d84000" = {},
  "imvu_qa" = {},
  "imvu_it" = {}

}



accounts = {
  "it" = {
    "name" = "Together Labs"
    "email" = "aws@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "audit" = {
    "name" = "Audit"
    "email" = "aws-audit-mgmt@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "log_archive" = {
    "name" = "Log Archive"
    "email" = "aws-log-archive-mgmt@ops.tl"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_data_analysts" = {
    "name" = "IMVU DATA ANALYSTS"
    "email" = "aws+data-analysts@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_operations" = {
    "name" = "IMVU Operations"
    "email" = "aws+ops@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_cs_prod" = {
    "name" = "IMVU CS Prod"
    "email" = "aws+cs@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_data_engineering" = {
    "name" = "IMVU-DATA-ENGINEERING"
    "email" = "aws+data-engineering@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_stayup" = {
    "name" = "IMVU StayUp"
    "email" = "aws+stayup@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_infra" = {
    "name" = "IMVU Infra"
    "email" = "aws+infra@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "withme_labs" = {
    "name" = "WithMe Labs"
    "email" = "aws+withme@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "together_labs" = {
    "name" = "Together Labs"
    "email" = "aws@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_ego_services" = {
    "name" = "IMVU Ego Services"
    "email" = "aws+ego@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_ego_dev" = {
    "name" = "IMVU Ego Dev"
    "email" = "aws+ego+dev@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_data_integration" = {
    "name" = "IMVU Data Integrations"
    "email" = "aws+data-engineering-int@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_databricks_d84000" = {
    "name" = "IMVU Databricks D84000"
    "email" = "aws+databricks@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_qa" = {
    "name" = "IMVU QA"
    "email" = "aws+qa@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  },
  "imvu_it" = {
    "name" = "IMVU IT"
    "email" = "aws+it@imvu.com"
    "role" = "AWSServiceRoleForOrganizations"
  }
}

