provider "aws" {
  region = var.provider_region
  default_tags {
    tags = local.global_tags
  }
}

module "ecr" {
  source = "../../../../../../modules/aws/ecr"
  repos  = var.repos
  principal_identifiers = var.ro_principal_identifiers
  account_id = data.aws_caller_identity.core-lib.account_id
  region = var.region
}



resource "aws_ecr_repository_policy" "ecr_access" {
  for_each = var.repos
  policy = data.aws_iam_policy_document.ecr_access[each.key].json
  repository = module.ecr.repos[each.key].name

  lifecycle {
    create_before_destroy = false
  }
}


data "aws_iam_policy_document" "ecr_access" {
  for_each = var.repos
  statement {
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:DescribeImages",
      "ecr:DescribeRegistry",
      "ecr:DescribeRepositories",
      "ecr:GetAuthorizationToken",
      "ecr:GetDownloadUrlForLayer",
      "ecr:GetLifecyclePolicy",
      "ecr:GetLifecyclePolicyPreview",
      "ecr:GetRegistryPolicy",
      "ecr:GetRepositoryPolicy",
      "ecr:ListImages",
      "ecr:ListTagsForResource"
    ]
    effect = "Allow"

    principals {
      identifiers = concat(var.ro_principal_identifiers, tolist(["arn:aws:iam::126252960572:role/xaccount-eks-ci"]))
      type = "AWS"
    }
  }
  statement {
    actions = [
        "ecr:PutImage",
        "ecr:TagResource",
        "ecr:UntagResource",
        "ecr:UploadLayerPart",
        "ecr:GetAuthorizationToken"
    ]
    effect = "Allow"

    principals {
      identifiers = ["arn:aws:iam::126252960572:role/xaccount-eks-ci"]
      type = "AWS"
    }
  }


}