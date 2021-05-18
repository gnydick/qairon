data "aws_caller_identity" "current" {}

locals {
  name_prefix = "${data.aws_caller_identity.current.account_id}-${var.environment}-"
}

module "iam_role_content_manager" {
  source = "../../../../../../../../modules/aws/iam-assumable-role-with-oidc"
  aws_account_id                = data.aws_caller_identity.current.account_id
  create_role                   = true
  force_detach_policies         = true
  max_session_duration          = 3600
  number_of_role_policy_arns    = 0
  oidc_fully_qualified_subjects =  ["system:serviceaccount:default:s3-content-manager", "system:serviceaccount:default:s3-content-manager2"]
  oidc_subjects_with_wildcards  = []
  provider_url                  = module.cluster.cluster_oidc_issuer_url
  provider_urls                 = []
  role_description              = "Role for use by content-manager microservice in EKS clsuter"
  role_name_prefix              = local.name_prefix
  role_path                     = "/"
  role_permissions_boundary_arn = ""
  role_policy_arns              = []
  tags = {
    "GeneratedBy" = "terraform"
    "Environment"= var.environment
  }

  depends_on = [module.cluster]
}

module "iam_policy_content_manager" {
  source = "../../../../../../../../modules/aws/iam-policy"
  description = "IAM Policy for content-manager IAM Role"
  iam_policy_document_actions = ["s3:ListBucket", "s3:GetBucketLocation", "s3:GetBucketAcl", "s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:PutObjectAcl"]
  iam_policy_document_effect = "Allow"
  iam_policy_document_resource_arn = [module.content_manager_s3.bucket_arn]
  iam_policy_document_sid = "1"
  iam_role_name = module.iam_role_content_manager.iam_role_name
  name = "content_manager_s3_rw"
  path = "/"
  tags = {
    "GeneratedBy" = "terraform"
    "Environment"= var.environment
  }
}