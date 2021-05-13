locals {
  aws_account_id = var.aws_account_id != "" ? var.aws_account_id : data.aws_caller_identity.current.account_id
  # clean URLs of https:// prefix
  urls = [
  for url in compact(distinct(concat(var.provider_urls, [var.provider_url]))) :
  replace(url, "https://", "")
  ]
  number_of_role_policy_arns = coalesce(var.number_of_role_policy_arns, length(var.role_policy_arns))
}