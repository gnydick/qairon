resource "aws_ecr_repository" "aws_docker_repo" {
  for_each = var.repos
  name = each.key
  image_scanning_configuration {
    scan_on_push = true
  }

}

resource "aws_ecr_repository_policy" "ro_ecr_access" {
  for_each = var.repos
  policy = data.aws_iam_policy_document.ro_ecr_access [each.key].json
  repository = aws_ecr_repository.aws_docker_repo[each.key].name
}


data "aws_iam_policy_document" "ro_ecr_access" {
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
      identifiers = var.principal_identifiers
      type = "AWS"
    }
  }


}

